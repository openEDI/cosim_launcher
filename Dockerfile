FROM ubuntu:24.04
RUN apt update && apt -y upgrade

# python deps
RUN apt install -y python3 python3-pip python3-virtualenv zip wget git
RUN mkdir ~/venv && cd ~/venv && virtualenv cosim_launcher

COPY . /home/cosim_launcher
RUN /bin/bash -c 'source ~/venv/cosim_launcher/bin/activate && cd /home/cosim_launcher/ && python3 -m pip install -e .'

ENTRYPOINT ["/bin/bash", "-c","source ~/venv/cosim_launcher/bin/activate && python3 /home/cosim_launcher/cosim_launcher/microservice/server.py"]
