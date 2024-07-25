# fermi-tutorial-docker
Docker package for fermi tutorial

## Installation instructions

Firstly clone this repo into a new directory called "fermi-tutorial-docker" e.g.

```git clone https://github.com/durhamgamma/fermi-tutorial-docker.git fermi-tutorial-docker```

Navigate into the newly created "fermi-tutorial-docker" directory and build the docker container e.g.:

```docker build --build-arg condaEnvFile=./tutorial-environment.yml --build-arg condaEnvName="fermipy-v1-0-1" -t fermi-tutorial:v1-0-0 .```

If you are building on an Apple Mac with the new ARM64 silicon achitecture (i.e. M1, M2 and M3 etc.) then you need to make sure Rosetta 2 is enabled on your machine for Intel x86_64 emulation. To check if Rosetta 2 is running on your computer run the following command in the terminal:

```if /usr/bin/pgrep -q oahd; then echo 'rosetta installed'; fi```

Usually you are prompted to install Rosetta 2 when you try to open an application that requires it. You may need to follow Apple's advice if you have any issues. In addition, you also need to ensure that the "Use Rosetta for x86_64/amd64 emulation on Apple Silicon" option is enabled in Docker Desktop application under Settings -> General. Lastly, when building the image you must provide the --platform option e.g.:

```docker build --platform linux/amd64 --build-arg condaEnvFile=./tutorial-environment.yml --build-arg condaEnvName="fermipy-v1-0-1" -t fermi-tutorial:v1-0-0 .```

## Dependencies

In order to build the docker container you need to have [Docker](https://www.docker.com) installed.

## Running the docker container for the tutorials in the [fermi-tutorial](https://github.com/durhamgamma/fermi-tutorial) repo

To run the newly created "fermi-tutorial:v1-0-0" docker image starting in the shell. Simply open a new terminal window and run:

```docker run -it --platform linux/amd64 --rm -v $PWD:/workdir -w /workdir --entrypoint /bin/bash fermi-tutorial:v1-0-0```

Note: Your system may require you to include a -c flag before the image name, and if you're running on an M-series Apple Mac computer you must provide the "--platform linux/amd64" option.

To run the newly created docker image starting in a Jupyter notebook, simply open a new terminal window and run:

```docker run -it --platform linux/amd64 --rm -p 8888:8888 -v $PWD:/workdir -w /workdir fermi-tutorial:v1-0-0```

## Notes:

Tutorial 2 in the [fermi-tutorial](https://github.com/durhamgamma/fermi-tutorial) repo requires you to run both the Jupyter notebook and complete exercises on the command line. You can do this simply by opening 2 new terminal windows and launching docker in one of them to start in a notebook and launching docker in the other to start from the shell.

Hint: After cloning this repository and successfully building the docker image, clone the [fermi-tutorial](https://github.com/durhamgamma/fermi-tutorial) repo into a new separate directory. Then navigate to where
cloned the [fermi-tutorial](https://github.com/durhamgamma/fermi-tutorial) repo and launch the docker image using the docker run commands shown above. This way the docker image will have access to all the tutorial files mounted in the /workdir directory.

## Usage:

If this Docker image is used to perform any analysis that is subsequently published, then please include the following acknowledgment:

*"We would like to acknowledge Cameron Rulten and Sheridan Lloyd of Durham University for providing the Docker image, and without this, this analysis would not be possible."*
