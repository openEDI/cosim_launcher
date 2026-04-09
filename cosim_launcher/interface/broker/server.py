import json
import os
import random
import socket
import shlex
import subprocess
import uuid
import sys
import logging
from http import HTTPStatus
from importlib.util import find_spec

import psutil
from flask import Flask, Response, request

from data_model import StaticInputs



formatStr='%(asctime)s::%(name)s::%(filename)s::%(funcName)s::'+\
	'%(levelname)s::%(message)s::%(threadName)s::%(process)d'
logging.basicConfig(stream=sys.stdout,level=logging.INFO,format=formatStr)
logger=logging.getLogger(__name__)


procMap={}
baseDir=os.path.dirname(os.path.abspath(__file__))


#=======================================================================================================================
def run():
	data=request.json
	staticInputs=StaticInputs(**data['static_inputs']).model_dump()

	runUUID=uuid.uuid4().hex

	dirPath=f'/tmp/{runUUID}'
	directive=f'mkdir -p {dirPath} && cp -r {baseDir}/* {dirPath}'
	flag=os.system(directive)
	assert flag==0

	# resolve
	fpath=f'/tmp/ip_{runUUID}.txt'
	os.system("ifconfig eth0 | grep 'inet ' | awk '{print $2}' > "+f"{fpath}")
	f=open(fpath); brokerHostIp=f.read().splitlines()[0]; f.close()
	os.system(f'rm {fpath}')

	portAssignment=assign_broker_port()
	success=False
	brokerDirective=f'helics_broker --loglevel=trace --all -f {staticInputs["number_of_federates"]} '
	brokerDirective+=f'--terminate_on_error=true '
	if portAssignment['success']:
		brokerDirective+=f'--port={portAssignment["port"]} '

		logger.info(f'brokerDirective::::{brokerDirective}')
		outfile=open(os.path.join(dirPath,'out.txt'),'w')
		errfile=open(os.path.join(dirPath,'error.txt'),'w')
		proc=subprocess.Popen(shlex.split(brokerDirective),stdout=outfile,stderr=errfile)
		procMap[runUUID]=proc.pid

		res=Response(status=HTTPStatus.OK)
		res.mimetype='application/json'
		res.response=json.dumps({"success":True,"uuid":runUUID,'broker_host_ip':brokerHostIp,\
			'broker_port':portAssignment["port"]})
		return res
	else:
		res=Response(status=HTTPStatus(500))
		res.mimetype='application/json'
		res.response=json.dumps({"success":False})
		return res

#=======================================================================================================================
def status():
	runUUID = request.args.get('uuid')
	if runUUID in procMap:
		procStatus='completed'
		procExists=psutil.pid_exists(procMap[runUUID])
		if procExists:
			p=psutil.Process(procMap[runUUID])
			if p.status()!='zombie':
				procStatus='running'
		res=Response(status=HTTPStatus.OK)
		res.mimetype='application/json'
		res.response=json.dumps({"success":True,"status":procStatus})
	else:
		res=Response(status=HTTPStatus.BAD_REQUEST)
		res.mimetype='application/json'
		res.response=json.dumps({"success":False,"error":f"UUID {runUUID} does not exist"})
	return res


#=======================================================================================================================
def logs():
	runUUID = request.args.get('uuid')
	dirpath=f'/tmp/{runUUID}'
	outfile=os.path.join(dirpath,'out.txt')
	errfile=os.path.join(dirpath,'error.txt')
	if os.path.exists(outfile) and os.path.exists(errfile):
		data={}
		f=open(outfile); data['outfile']=f.read(); f.close()
		f=open(errfile); data['errfile']=f.read(); f.close()
		res=Response(status=HTTPStatus.OK)
		res.mimetype='application/json'
		res.response=json.dumps({"success":True,"info":data})
	else:
		res=Response(status=HTTPStatus.BAD_REQUEST)
		res.mimetype='application/json'
		res.response=json.dumps({"success":False,"error":f"UUID {runUUID} does not exist on file system"})
	return res


#=======================================================================================================================
def get_helics_broker_ports_in_use():
	fname=uuid.uuid4().hex
	os.system("netstat -tap | grep helics_broker | awk '{print $4}' | awk -F ':' '{print $2}' > "+f"{fname}")
	f=open(fname);usedPorts=[int(p) for p in f.read().splitlines()]; f.close()
	usedPorts.sort()
	os.system(f'rm {fname}')
	return usedPorts

#=======================================================================================================================
def assign_broker_port(portMin=10000,portMax=40000):
	usedPorts=get_helics_broker_ports_in_use()
	brokerPorts=list(set(range(portMin,portMax)).difference(usedPorts))
	ind=random.randint(0,len(brokerPorts)-1)

	success=False
	tries,maxTries=0,100
	while not success:# helics_broker requires port and port+1
		brokerPort=brokerPorts[ind]
		if brokerPort+1 in brokerPorts:
			success=True
		tries+=1
		if tries>=maxTries:
			break
	brokerPort=brokerPorts[ind] if success else -1

	return {'success':success,'port':brokerPort}


#=======================================================================================================================
if __name__ == '__main__':
	app = Flask(__name__)
	app.add_url_rule(rule='/run',methods=['POST'],view_func=run)
	app.add_url_rule(rule='/status',methods=['GET'],view_func=status)
	app.add_url_rule(rule='/logs',methods=['GET'],view_func=logs)
	app.run(host='0.0.0.0',port=5200,debug=False,use_reloader=False,threaded=True)

