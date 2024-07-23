# syntax=docker/dockerfile:1
# This is the python 3 version in preparation for the
# long awaited fermitools transition to py3
# NOTE: When building this docker image make sure you increase your RAM and Swap
# file size in your docker preferences otherwise you'll get lots of build failures

FROM ubuntu:20.04 AS builder
LABEL org.opencontainers.image.authors="Cameron Rulten <cameron.b.rulten@durham.ac.uk>"

ARG TARGETPLATFORM
ARG os_name
ARG condaEnvFile
ARG condaEnvName="fermipy-v1-0-1"
ARG whichConda

RUN echo "Building Docker image for - Plaform: ${TARGETPLATFORM}"

# System packages
RUN apt-get update && apt-get install -y curl \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

# Install miniconda to /miniconda
#RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
#RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda3 -b
#RUN rm Miniconda3-latest-Linux-x86_64.sh
#ENV PATH=/miniconda3/bin:${PATH}

# RUN if [ "${os_name}" = "Darwin"]; then \
#         whichConda="Miniforge3-MacOSX-arm64" \
#     else \
#         whichConda="Miniforge3-MacOSX-arm64" \

COPY miniforge-setup.sh /
RUN chmod u+x /miniforge-setup.sh && /miniforge-setup.sh "${TARGETPLATFORM}"
#RUN curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"
#RUN bash Miniforge3-Linux-x86_64.sh -p /miniforge3 -b
#RUN url -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
#RUN bash Miniforge3-$(uname)-$(uname -m).sh -p /miniforge3 -b

#RUN rm Miniforge3-Linux-x86_64.sh
ENV PATH=/miniforge3/bin:${PATH}
RUN conda update -y conda

#Append conda-forge channel
#RUN conda config --append channels conda-forge

#RUN conda install --yes -c conda-forge mamba gosu tini ipykernel
RUN mamba install --yes -c conda-forge gosu tini ipykernel

# Python packages from conda
# RUN conda install -y \
# numpy==1.16
# astropy \
# scipy \
# matplotlib \
# pyyaml \
# ipython \
# jupyter
#
#Copy conda environment file to newly created temp directory
#RUN mkdir /temp
WORKDIR /temp
#COPY tutorial-environment.yml .
COPY $condaEnvFile .
#Create conda fermi environment
#RUN conda env create -f tutorial-environment.yml
RUN mamba env create -f $condaEnvFile


SHELL ["conda", "run", "-n", "fermipy-v1-0-1", "/bin/bash", "-c"]
# RUN conda install -n $condaEnvName fermipy \
# && python -m ipykernel install --user --name=$condaEnvName
RUN python -m ipykernel install --user --name=$condaEnvName

#Set up paths
WORKDIR /workdir
#RUN mkdir /workdir
#&& mkdir /home/fermi-external/diffuseModels/

#ENV FERMI_DIFFUSE_DIR=/home/externals/diffuseModels/v5r0
ENV FERMI_DIFFUSE_DIR=/miniforge3/envs/$condaEnvName/share/fermitools/refdata/fermi/galdiffuse
#ENV SLAC_ST_BUILD=true
#ENV INST_DIR=/miniconda/share/fermitools
ENV FERMI_DIR=/miniforge3/envs/$condaEnvName/share/fermitools/
#ENV GLAST_EXT=/home/externals
ENV MATPLOTLIBRC=/home/matplotlib
#Set environmnet variables which don't appear to get set
ENV CALDB=/miniforge3/envs/$condaEnvName/share/fermitools/data/caldb
ENV CALDBROOT=/miniforge3/envs/$condaEnvName/share/fermitools/data/caldb
ENV CALDBALIAS=/miniforge3/envs/$condaEnvName/share/fermitools/data/caldb/software/tools/alias_config.fits
ENV CALDBCONFIG=/miniforge3/envs/$condaEnvName/share/fermitools/data/caldb/software/tools/caldb.config


WORKDIR /home/matplotlib
RUN echo "backend      : Agg" >> /home/matplotlib/matplotlibrc


#Copy the locally updated 4FGL-DR2 catalog into the fermipy catalog directory
#This local copy of the catalog changes the incorrectly named PLSuperExpCutoff with PLSuperExpCutoff2
WORKDIR /miniforge3/envs/$condaEnvName/lib/python3.10/site-packages/fermipy/data/catalogs
COPY gll_psc_v27.fit /miniforge3/envs/$condaEnvName/lib/python3.10/site-packages/fermipy/data/catalogs

#Copy the locally updated fermipy files into the container fermipy installation
#The updated catalog file reflects the use of the gll_psc_v27.fit catalog files
#when using the "4FGL" keyword in your analysis config.pyaml file.
#The updated ltcube.py file reflects the TSTART and TSTOP fits file changes causing key error
#The updated lightcurve.py file now checks for a fit where failure to check can cause the "fit_success" key error
WORKDIR /miniforge3/envs/$condaEnvName/lib/python3.10/site-packages/fermipy
RUN rm -f lightcurve.py
COPY catalog.py ltcube.py lightcurve.py ./


WORKDIR /workdir
ENV FERMIPY=/miniforge3/envs/$condaEnvName/lib/python3.10/site-packages/fermipy/

#RUN mkdir /home/pfiles
#ENV PFILES=/home/pfiles


WORKDIR /home
#Add the tutorial data to the docker container
#COPY fermi-tutorial.tar.gz .
#RUN tar -xvzf fermi-tutorial.tar.gz -C . && rm fermi-tutorial.tar.gz
RUN env | grep -w "PFILES" > env-logon.list
#VOLUME /home/fermi-tutorial


WORKDIR /temp
COPY ./entrypoint.sh ./start-env.py ./
RUN chmod 755 entrypoint.sh

WORKDIR /workdir
EXPOSE 8888


SHELL ["/bin/bash", "-c"]
# Give bash access to Anaconda
RUN echo "source activate $condaEnvName" >> ~/.bashrc && \
    source ~/.bashrc

ENV PATH=/miniforge3/envs/fermipy-v1-0-1/bin:$PATH

# ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "fermipy-v1-0-1", "jupyter-lab", "--notebook-dir=/workdir", "--ip='0.0.0.0'", "--port=8888", "--no-browser", "--allow-root"]
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "fermipy-v1-0-1", "jupyter", "notebook", "--notebook-dir=/workdir", "--ip='0.0.0.0'", "--port=8888", "--no-browser", "--allow-root"]
#ENTRYPOINT ["/bin/bash","--login","-c"]



##End of Dockerfile
