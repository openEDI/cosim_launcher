import json
import os
import shlex
import subprocess
import uuid
from http import HTTPStatus
from importlib.util import find_spec
import sys
import pdb
import logging
import asyncio

import psutil
import requests
from flask import Flask, Response, request
import httpx
from oedisi.componentframework.basic_component import ComponentDescription, basic_component
from oedisi.componentframework.system_configuration import generate_runner_config
from oedisi.componentframework.system_configuration import WiringDiagram as WiringDiagramChecker

from cosim_launcher.microservice.data_model import WiringDiagram


formatStr='%(asctime)s::%(name)s::%(filename)s::%(funcName)s::'+\
	'%(levelname)s::%(message)s::%(threadName)s::%(process)d'
logging.basicConfig(stream=sys.stdout,level=logging.INFO,format=formatStr)
logger=logging.getLogger(__name__)

baseDir=os.path.dirname(os.path.abspath(__file__))
services=json.load(open(os.path.join(baseDir,'services.json')))
componentData=json.load(open(os.path.join(baseDir,'components.json')))

uuidMap={}
serviceMap={}


#=======================================================================================================================
def run():
	data=request.json
	data=WiringDiagram(**data).model_dump()

	# TODO: Disabling wiring_diagram_checker as the current approach uses generate_runner_config(),
	# which uses oedisi.componentframework.system_configuration.initialize_federates(). However,
	# only a portion of this logic is needed. The approach as is also copies files and this results in
	# response time going from < 1 second to 3-4 seconds.
#	isValid=wiring_diagram_checker(data,componentData)
#	if not isValid:
#		logger.info(f'wiring diagram check failed')
#		res=Response(status=HTTPStatus(422))
#		res.mimetype='application/json'
#		res.response=json.dumps({'success':False,'info':'invalid wiring diagram'})
#		return res

	# process data
	n2t=_algname2type(data['components'])
	staticInputs=_get_static_inputs(data['components'])
	inputMapping=_get_input_mapping(data['links'])

	cosimPayloadData={}
	for k in n2t:
		cosimPayloadData[k]={'input_mapping':{},'type':n2t[k]}
		cosimPayloadData[k].update(services[n2t[k]])
		cosimPayloadData[k]['static_inputs']=staticInputs[k]
		if k in inputMapping:
			cosimPayloadData[k]['input_mapping']=inputMapping[k]

	runUUID=uuid.uuid4().hex
	uuidMap[runUUID]={}
	serviceMap[runUUID]={}
	brokerUrl=f'http://{services["Broker"]["hostname"]}:{services["Broker"]["port"]}/run'

	# send info to broker
	nFed=len(staticInputs.keys())
	brokerServerReply=requests.post(brokerUrl,json={'static_inputs':{'number_of_federates':nFed}})
	uuidMap[runUUID]['broker']=brokerServerReply.json()
	serviceMap[runUUID]['broker']={'hostname':services["Broker"]["hostname"],\
		'port':services["Broker"]["port"]}

	cosimBrokerIp=uuidMap[runUUID]['broker']['broker_host_ip']
	cosimBrokerPort=uuidMap[runUUID]['broker']['broker_port']

	if brokerServerReply.status_code!=200:
		res=Response(status=HTTPStatus(500))
		res.mimetype='application/json'
		res.response=json.dumps({'success':False,'error':{'url':brokerUrl,'info':brokerServerReply.text(),\
			'status_code':brokerServerReply.status_code}})
		return res

	success=True
	msg={}
	for k in cosimPayloadData:
		payload={'static_inputs':cosimPayloadData[k]['static_inputs'],\
			'input_mapping':cosimPayloadData[k]['input_mapping']}
		payload['static_inputs']['broker_address']=cosimBrokerIp
		payload['static_inputs']['port']=cosimBrokerPort
		serviceHost=cosimPayloadData[k]['hostname']
		servicePort=cosimPayloadData[k]['port']
		serviceMap[runUUID][k]={'hostname':serviceHost,'port':servicePort}
		url=f'http://{serviceHost}:{servicePort}'
		res=requests.post(url=url+'/run',json=payload)
		uuidMap[runUUID][k]=res.json() # store for later use
		if res.status_code!=200:
			success=False
			msg['error']={'url':url,'info':res.text(),'status_code':res.status_code}
			break

	if success:
		res=Response(status=HTTPStatus.OK)
		res.mimetype='application/json'
		res.response=json.dumps({"success":True,"uuid":runUUID,"info":uuidMap[runUUID]})
	else:
		res=Response(status=HTTPStatus(500))
		res.mimetype='application/json'
		res.response=json.dumps(msg)

	return res

#=======================================================================================================================
def _algname2type(components):
	mapped={}
	for entry in components:
		mapped[entry['name']]=entry['type']
	return mapped

#=======================================================================================================================
def _get_static_inputs(components):
	res={}
	for entry in components:
		res[entry['name']]=entry['parameters']
		res[entry['name']]['name']=entry['name']
	return res

#=======================================================================================================================
def _get_input_mapping(links):
	res={}
	for entry in links:
		if entry['target'] not in res:
			res[entry['target']]={}
		res[entry['target']][entry['target_port']]=f"{entry['source']}/{entry['source_port']}"
	return res

#=======================================================================================================================
def status():
	runUUID = request.args.get('uuid')

	res=Response(status=HTTPStatus.OK)
	res.mimetype='application/json'

	data={}
	for entry in serviceMap[runUUID]:
		serviceHost=serviceMap[runUUID][entry]['hostname']
		servicePort=serviceMap[runUUID][entry]['port']
		url=f'http://{serviceHost}:{servicePort}'
		reply=requests.get(url=url+'/status',params={'uuid':uuidMap[runUUID][entry]['uuid']})
		data[entry]=reply.json()

	res.response=json.dumps({"success":True,"info":data})
	return res

#=======================================================================================================================
async def logs():
	runUUID = request.args.get('uuid')

	res=Response(status=HTTPStatus.OK)
	res.mimetype='application/json'

	data={}
	urls,params=[],[]
	entries=list(serviceMap[runUUID].keys())
	for entry in entries:
		serviceHost=serviceMap[runUUID][entry]['hostname']
		servicePort=serviceMap[runUUID][entry]['port']
		urls.append(f'http://{serviceHost}:{servicePort}/logs')
		params.append({'uuid':uuidMap[runUUID][entry]['uuid']})

	async with httpx.AsyncClient() as client:
		replies=await asyncio.gather(*[client.get(url=url,params=param) for url,param in zip(urls,params)])
		for entry,reply in zip(entries,replies):
			data[entry]=reply.json()

	res.response=json.dumps({"success":True,"info":data})
	return res

#=======================================================================================================================
async def results():
	runUUID = request.args.get('uuid')

	res=Response(status=HTTPStatus.OK)
	res.mimetype='application/json'

	data={}
	urls,params=[],[]
	entries=list(serviceMap[runUUID].keys())
	recorderFeds=[]
	for entry in entries:
		if 'recorder_' in entry:
			serviceHost=serviceMap[runUUID][entry]['hostname']
			servicePort=serviceMap[runUUID][entry]['port']
			urls.append(f'http://{serviceHost}:{servicePort}/results')
			params.append({'uuid':uuidMap[runUUID][entry]['uuid']})
			recorderFeds.append(entry)

	async with httpx.AsyncClient() as client:
		replies=await asyncio.gather(*[client.get(url=url,params=param) for url,param in zip(urls,params)])
		for entry,reply in zip(recorderFeds,replies):
			data[entry]=reply.json()

	res.response=json.dumps({"success":True,"info":data})
	return res

#=======================================================================================================================
def wiring_diagram_checker(wiringDiagram,componentData):
	try:
		component_types = {}
		for entry in componentData:
			item=ComponentDescription.model_validate(componentData[entry])
			item.directory='./'
			component_types[entry]=basic_component(item,True)

		runner_config = generate_runner_config(WiringDiagramChecker.model_validate(wiringDiagram),\
			component_types, target_directory='/tmp')
		return True
	except:
		return False

#=======================================================================================================================
if __name__ == '__main__':
	app = Flask(__name__)
	app.add_url_rule(rule='/run',methods=['POST'],view_func=run)
	app.add_url_rule(rule='/status',methods=['GET'],view_func=status)
	app.add_url_rule(rule='/logs',methods=['GET'],view_func=logs)
	app.add_url_rule(rule='/results',methods=['GET'],view_func=results)
	app.run(host='0.0.0.0',port=5100,debug=False,use_reloader=False,threaded=True)


