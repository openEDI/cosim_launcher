FROM ubuntu:24.04
RUN apt update && apt -y upgrade

# python deps
RUN apt install -y python3 python3-pip python3-virtualenv zip wget git net-tools
RUN mkdir ~/venv && cd ~/venv && virtualenv broker

# install
RUN /bin/bash -c 'source ~/venv/broker/bin/activate && python3 -m pip install psutil>=7.2.2 flask>=3.1.3 pydantic>=2.12.5 helics>=3.6.1'

COPY . /home/broker

ENTRYPOINT ["/bin/bash", "-c","source ~/venv/broker/bin/activate && python3 /home/broker/server.py"]
