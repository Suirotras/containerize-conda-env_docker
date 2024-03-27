# syntax=docker/dockerfile:1
FROM phusion/baseimage:jammy-1.0.2

### Copy the packed_env.tar to the container
COPY packed_env.tar /packed_env.tar

### set environment variable
ENV NUMBA_CACHE_DIR="/tmp/numba_cache"

### Run commands to install miniconda and to activate the conda environment

## install tar
RUN apt-get install -y tar
## install miniconda3
RUN curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh > /install_conda.sh && \
    chmod +x /install_conda.sh && \
    /install_conda.sh -b -p /opt/conda && \
    rm /install_conda.sh
## unpack the packed_env.tar
RUN tar xf /packed_env.tar && \
    rm /packed_env.tar

## Activate the conda environment and run the bash shell upon container start
ENTRYPOINT ["bash", "-c", "source /opt/conda/bin/activate {conda_env} && tail -f /dev/null"]
