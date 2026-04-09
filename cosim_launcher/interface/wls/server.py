import json
import os
import shlex
import subprocess
import uuid
import argparse
from http import HTTPStatus
from importlib.util import find_spec

import psutil
from flask import Flask, Response, request

from data_model import StaticInputs, InputMapping

procMap={}


#=======================================================================================================================
def run():
	data=request.json
	assert not set(['static_inputs','input_mapping']).difference(data.keys())
	inputMapping=InputMapping(**data['input_mapping']).model_dump()
	staticInputs=StaticInputs(**data['static_inputs']).model_dump()

	runUUID=uuid.uuid4().hex
	brokerAddress=staticInputs['broker_address']
	brokerPort=staticInputs['port']

	dirPath=f'/tmp/{runUUID}'
	directive=f'mkdir -p {dirPath} && cp -r {LIB_PATH}/* {dirPath}'
	flag=os.system(directive)
	assert flag==0

	# update based on payload
	json.dump(staticInputs,open(os.path.join(dirPath,'static_inputs.json'),'w'))
	json.dump(inputMapping,open(os.path.join(dirPath,'input_mapping.json'),'w'))

	runPath=os.path.join(dirPath,'state_estimator_federate.py')
	directive=f'python3 {runPath} -i {brokerAddress} -p {brokerPort}'
	outfile=open(os.path.join(dirPath,'out.txt'),'w')
	errfile=open(os.path.join(dirPath,'error.txt'),'w')
	proc=subprocess.Popen(shlex.split(directive),stdout=outfile,stderr=errfile,cwd=dirPath)
	procMap[runUUID]=proc.pid

	res=Response(status=HTTPStatus.OK)
	res.mimetype='application/json'
	res.response=json.dumps({"success":True,"uuid":runUUID})
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
	staticInputsFile=os.path.join(dirpath,'static_inputs.json')
	inputMappingFile=os.path.join(dirpath,'input_mapping.json')
	if os.path.exists(outfile) and os.path.exists(errfile) and \
		os.path.exists(staticInputsFile) and os.path.exists(inputMappingFile):
		data={}
		f=open(outfile); data['outfile']=f.read(); f.close()
		f=open(errfile); data['errfile']=f.read(); f.close()
		f=open(staticInputsFile); data['static_inputs']=f.read(); f.close()
		f=open(inputMappingFile); data['input_mapping']=f.read(); f.close()
		res=Response(status=HTTPStatus.OK)
		res.mimetype='application/json'
		res.response=json.dumps({"success":True,"info":data})
	else:
		res=Response(status=HTTPStatus.BAD_REQUEST)
		res.mimetype='application/json'
		res.response=json.dumps({"success":False,"error":f"UUID {runUUID} does not exist on file system"})
	return res


#=======================================================================================================================
if __name__ == '__main__':
	parser=argparse.ArgumentParser()
	parser.add_argument('-l','--libpath',help='localfeeder library path',required=True)
	args=parser.parse_args()

	LIB_PATH=args.libpath

	app = Flask(__name__)
	app.add_url_rule(rule='/run',methods=['POST'],view_func=run)
	app.add_url_rule(rule='/status',methods=['GET'],view_func=status)
	app.add_url_rule(rule='/logs',methods=['GET'],view_func=logs)
	app.run(host='0.0.0.0',port=5000,debug=False,use_reloader=False,threaded=True)

