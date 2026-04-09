FROM ubuntu:24.04
RUN apt update && apt -y upgrade

RUN apt install -y python3 python3-pip python3-virtualenv zip git net-tools
RUN mkdir ~/venv && cd ~/venv && virtualenv sensor

RUN cd /home && git clone --branch v0.6.0 --depth 1 https://github.com/openEDI/oedisi-example.git

RUN /bin/bash -c 'source ~/venv/sensor/bin/activate && \
	cd /home/oedisi-example/measuring_federate && \
	python3 -m pip install -r requirements.txt'

RUN /bin/bash -c 'source ~/venv/sensor/bin/activate && \
	python3 -m pip install flask psutil'

COPY . /home/sensor

RUN cd /home/oedisi-example/measuring_federate && patch < /home/sensor/sensor.patch


ENTRYPOINT ["/bin/bash", "-c","source ~/venv/sensor/bin/activate && python3 /home/sensor/server.py -l /home/oedisi-example/measuring_federate"]
