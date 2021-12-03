# fermi-tutorial-docker
Docker package for fermi tutorial

## Installation instructions

Firstly clone this repo into a new directory called "fermi-tutorial-docker" e.g.

```git clone https://github.com/durhamgamma/fermi-tutorial-docker.git fermi-tutorial-docker```

Navigate into the newly created "fermi-tutorial-docker" directory and build the docker container as follows:

```docker build --build-arg condaEnvFile=./tutorial-environment.yml --build-arg condaEnvName="fermipy-v1-0-1" -t fermi-tutorial:v1-0-0 .```

## Dependencies

In order to build the docker container you need to have [Docker](https://www.docker.com) installed.

## Running the docker container for the tutorials in the [fermi-tutorial](https://github.com/durhamgamma/fermi-tutorial) repo

To run the newly created "fermi-tutorial:v1-0-0" docker image starting in the shell. Simply open a new terminal window and run:

```docker run -it --rm -v $PWD:/workdir -w /workdir --entrypoint /bin/bash fermi-tutorial:v1-0-0```

Note: Your system may require you to include a -c flag before the image name

To run the newly created docker image starting in a Jupyter notebook, simply open a new terminal window and run:

```docker run -it --rm -p 8888:8888 -v $PWD:/workdir -w /workdir fermi-tutorial:v1-0-0```

## Notes:

Tutorial 2 in the [fermi-tutorial](https://github.com/durhamgamma/fermi-tutorial) repo requires you to run both the Jupyter notebook and complete exercises on the command line. You can do this simply by opening 2 new terminal windows and launching docker in one of them to start in a notebook and launching docker in the other to start from the shell.
