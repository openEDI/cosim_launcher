FROM python:3.11.18-slim-trixie
RUN apt update && apt -y upgrade
RUN cd /home && python3 -m venv venv
RUN /bin/bash -c 'cd /home && source /home/venv/bin/activate && pip install --upgrade pip && pip install tensorflow-cpu'
