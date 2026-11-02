import time
import argparse

import requests


if __name__=='__main__':
	parser=argparse.ArgumentParser()
	parser.add_argument('-u','--uuid',help='uuid',required=True)
	parser.add_argument('--url',help='url',required=True)
	parser.add_argument('-w','--walltime',help='wait time in seconds',required=True)
	args=parser.parse_args()

	time.sleep(float(args.walltime))
	res=requests.get(url=args.url+'/sigterm',params={'uuid':args.uuid})
