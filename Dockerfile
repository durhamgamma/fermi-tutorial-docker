# syntax=docker/dockerfile:1
# Dockerfile for fermitools and fermipy
# NOTE: When building this docker image make sure you increase your RAM and Swap
# file size in your docker preferences otherwise you'll get lots of build failures

FROM ubuntu:20.04
LABEL org.opencontainers.image.authors="Cameron Rulten <cameron.b.rulten@durham.ac.uk>"

#define some environment variables
ARG condaEnvFile
ARG condaEnvName="fermipy-v1-2-2"

# Update and install some useful system packages
RUN apt-get -y update --no-install-recommends && \
apt-get -y install --no-install-recommends curl ca-certificates && \
apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install miniconda to /miniconda
RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    chmod +x Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda3 -b && \
    rm Miniconda3-latest-Linux-x86_64.sh

ENV PATH=/miniconda3/bin:${PATH}
RUN conda update -y conda

#Append conda-forge channel and install some tools
RUN conda config --append channels conda-forge && \
    conda install --yes -c conda-forge mamba gosu tini ipykernel

#Copy conda environment file into temp directory
WORKDIR /temp
COPY $condaEnvFile .

#Create conda fermi environment using mamba
#RUN conda env create -f tutorial-environment.yml
RUN mamba env create -f $condaEnvFile

#Set up Fermitools paths
WORKDIR /workdir

# Ensure that Conda is sourced and activate the environment in any new shell session
RUN echo "source /miniconda3/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate $condaEnvName" >> ~/.bashrc && \
    echo "source ~/.bashrc" >> /etc/bash.bashrc

# Set up the environment for matplotlib
WORKDIR /home/matplotlib
RUN echo "backend      : Agg" >> /home/matplotlib/matplotlibrc

# Set up two useful fermipy environment variables and copy a version of the catalog into a new directory
# for the tutorial
WORKDIR /workdir
ENV FERMIPY=/miniconda3/envs/$condaEnvName/lib/python3.9/site-packages/fermipy/
ENV LATEXTDIR=/miniconda3/envs/$condaEnvName/lib/python3.9/site-packages/fermipy/data/catalogs
# Create the symbolic link to one of the catalog files in the /tutorial2_catalog
RUN mkdir /tutorial2_catalog && \
    ln -s $LATEXTDIR/gll_psc_v27.fit /tutorial2_catalog/gll_psc_v27.fit


# Open the port and set workdir permissions
WORKDIR /workdir
EXPOSE 8888
RUN chmod -R 777 /workdir


# Copy entrypoint.sh script into the temp directory, set permissions and create the entrypoint
WORKDIR /temp
COPY ./entrypoint.sh ./
RUN chmod 755 entrypoint.sh

# Use the entrypoint.sh script as the entrypoint
ENTRYPOINT ["/temp/entrypoint.sh"]




##End of Dockerfile
