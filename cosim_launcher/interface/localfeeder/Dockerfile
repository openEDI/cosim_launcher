FROM ubuntu:24.04
RUN apt update && apt -y upgrade

RUN apt install -y python3 python3-pip python3-virtualenv zip git net-tools
RUN mkdir ~/venv && cd ~/venv && virtualenv localfeeder

RUN cd /home && git clone --branch v0.6.0 --depth 1 https://github.com/openEDI/oedisi-example.git

RUN /bin/bash -c 'source ~/venv/localfeeder/bin/activate && \
	cd /home/oedisi-example/LocalFeeder && \
	python3 -m pip install -r requirements.txt'

RUN /bin/bash -c 'source ~/venv/localfeeder/bin/activate && \
	python3 -m pip install flask psutil'

COPY . /home/localfeeder

RUN cd /home/oedisi-example/LocalFeeder && patch < /home/localfeeder/localfeeder.patch


ENTRYPOINT ["/bin/bash", "-c","cp -r /home/localfeeder/oedisi_smartds_cache /tmp && cd /tmp/oedisi_smartds_cache && unzip -q \"/tmp/oedisi_smartds_cache/*.zip\" && source ~/venv/localfeeder/bin/activate && python3 /home/localfeeder/server.py -l /home/oedisi-example/LocalFeeder"]
