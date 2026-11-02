FROM python:3.11.18-slim-trixie
RUN apt update && apt -y upgrade
RUN apt install -y wget git
RUN cd /home && python3 -m venv venv
RUN cd /home && wget https://download-r2.pytorch.org/whl/cpu/torch-2.9.0%2Bcpu-cp311-cp311-manylinux_2_28_x86_64.whl#sha256=add3e93ecc1eeaa6853f6a973ce60ffb3cb14ed2e80f5055e139b09385dce0a7
RUN /bin/bash -c 'cd /home && source /home/venv/bin/activate && pip install --upgrade pip && pip install torch-2.9.0+cpu-cp311-cp311-manylinux_2_28_x86_64.whl && rm /home/torch-2.9.0+cpu-cp311-cp311-manylinux_2_28_x86_64.whl'
RUN cd /home && git clone --depth=1 https://github.com/openEDI/ornl-imputation.git
RUN /bin/bash -c 'cd /home/ornl-imputation && source /home/venv/bin/activate && pip install -e .'
