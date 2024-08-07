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


#You cannot use an environment variable inside a shell command like this
#Instead we need a workaround by creating a shell script
#SHELL ["conda", "run", "-n", $condaEnvName, "/bin/bash", "-c"]

# Create a shell script that uses the environment variable
RUN echo '#!/bin/bash\nconda run -n $condaEnvName /bin/bash -c "$@"' > /usr/local/bin/conda_shell.sh && \
    chmod +x /usr/local/bin/conda_shell.sh
SHELL ["/usr/local/bin/conda_shell.sh"]

RUN pip install fermipy
# RUN conda install -n $condaEnvName fermipy \
# && python -m ipykernel install --user --name=$condaEnvName
RUN python -m ipykernel install --user --name=$condaEnvName

#Set up paths
WORKDIR /workdir

#ENV FERMI_DIFFUSE_DIR=/home/externals/diffuseModels/v5r0
ENV FERMI_DIFFUSE_DIR=/miniconda3/envs/$condaEnvName/share/fermitools/refdata/fermi/galdiffuse
#ENV SLAC_ST_BUILD=true
#ENV INST_DIR=/miniconda/share/fermitools
ENV FERMI_DIR=/miniconda3/envs/$condaEnvName/share/fermitools/
#ENV GLAST_EXT=/home/externals
ENV MATPLOTLIBRC=/home/matplotlib
#Set environmnet variables which don't appear to get set
ENV CALDB=/miniconda3/envs/$condaEnvName/share/fermitools/data/caldb
ENV CALDBROOT=/miniconda3/envs/$condaEnvName/share/fermitools/data/caldb
ENV CALDBALIAS=/miniconda3/envs/$condaEnvName/share/fermitools/data/caldb/software/tools/alias_config.fits
ENV CALDBCONFIG=/miniconda3/envs/$condaEnvName/share/fermitools/data/caldb/software/tools/caldb.config


WORKDIR /home/matplotlib
RUN echo "backend      : Agg" >> /home/matplotlib/matplotlibrc

WORKDIR /workdir
ENV FERMIPY=/miniconda3/envs/$condaEnvName/lib/python3.9/site-packages/fermipy/
ENV LATEXTDIR=/miniconda3/envs/$condaEnvName/lib/python3.9/site-packages/fermipy/data/catalogs
# Create the symbolic link to one of the catalog files in the /tutorial2_catalog
RUN mkdir /tutorial2_catalog && \
    ln -s $LATEXTDIR/gll_psc_v27.fit /tutorial2_catalog/gll_psc_v27.fit

WORKDIR /home
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

ENV PATH=/miniconda3/envs/$condaEnvName/bin:$PATH

# Use the entrypoint.sh script as the entrypoint
ENTRYPOINT ["/temp/entrypoint.sh"]

# ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "fermipy-v1-2-2", "jupyter-lab", "--notebook-dir=/workdir", "--ip='0.0.0.0'", "--port=8888", "--no-browser", "--allow-root"]
#ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", $condaEnvName, "jupyter", "notebook", "--notebook-dir=/workdir", "--ip='0.0.0.0'", "--port=8888", "--no-browser", "--allow-root"]
#ENTRYPOINT ["/bin/bash","--login","-c"]



##End of Dockerfile
