# Send wiring diagram to cosim_launcher

```python
	from io import StringIO
	import json

	import requests
	import pandas as pd

	url='either local address (minikube) or external ip'

	data=json.load(open('cosim_launcher/wiring_diagram/nlpdsse_smartds_small.json'))
	res=requests.post(url=url+'/run',json=data)
	assert res.status_code==200
	info=res.json()

	# info/reply/output
	{'success': True,
	 'uuid': '29d7da8539454da5955b0d8e6c98f738',
	 'info': {'broker': {'success': True,
		'uuid': 'e68f50bca0e140b4ac849c3fee3e04e5',
		'broker_host_ip': '10.244.2.94',
		'broker_port': 17173},
	  'recorder_voltage_real': {'success': True,
		'uuid': 'd0608be41d384a99857111cd54886786'},
	  'recorder_voltage_imag': {'success': True,
		'uuid': '0a863a76cc534e6a9b5e713e3820b109'},
	  'recorder_voltage_mag': {'success': True,
		'uuid': '301cf58bf86048c386302b2f7b106c3d'},
	  'recorder_voltage_angle': {'success': True,
		'uuid': '6c3d2eb6601348f08cc467664404c697'},
	  'nlpdsse': {'success': True, 'uuid': 'cf784c8eeb17444baba791de52ed987d'},
	  'feeder': {'success': True, 'uuid': 'a0cb1562e0774b9eb2ffe74fbac65a20'},
	  'sensor_voltage_magnitude': {'success': True,
		'uuid': 'd8073d90fa8c4d75b0c483f686302c9b'},
	  'sensor_power_real': {'success': True,
		'uuid': '82bc89ba5678442495dbc63aaa844072'},
	  'sensor_power_imaginary': {'success': True,
		'uuid': 'b5599cc6d5a849a190fd370c4d50bc18'}}}
```

# Status

```python
	res=requests.get(url=url+'/status',params={'uuid':info['uuid']})
	assert res.status_code==200
	status=res.json()
```

# Logs

```python
	res=requests.get(url=url+'/logs',params={'uuid':info['uuid']})
	assert res.status_code==200
	logs=res.json()
```

# Results

```python
	res=requests.get(url=url+'/results',params={'uuid':info['uuid']})
	assert res.status_code==200
	results=res.json()

	# DataFrame
	df={entry:pd.read_csv(StringIO(results['info'][entry]['info'])) for entry in results['info']}
```

# Roadmap

* Migrate to production server
* Add Nginx
* AWS Migration


