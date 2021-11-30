# fermi-tutorial-docker
Docker package for fermi tutorial

## Tutorial files
Before you can build this docker container you need to make sure you have the fermi-tutorial tarball. You can generate the tarball by following the instructions in the README of the fermi-tutorial repo.

Once you have created the fermi-tutorial tarball, clone this repo into a new working directory that you will use to create the docker container e.g.

```git clone <git address> fermi-tutorial-docker```

Navigate into your working directory and copy the fermi-tutorial tarball into it e.g.

```cd fermi-tutorial-docker
cp ../fermi-tutorial/fermi-tutorial.tar.gz .```

Once this is done you can build the docker container as follows.

## To build the image
```docker build --build-arg condaEnvFile=./tutorial-environment.yml --build-arg condaEnvName="fermipy-v1-0-1" -t fermi-tutorial:v1-0-0 .```

## To run the newly created docker container starting in the shell (Your system may require you to include a -c flag before the image name):
```docker run -it --rm -v $PWD:/workdir -w /workdir --entrypoint /bin/bash fermi-tutorial:v1-0-0```

## To run the newly created docker container starting in a Jupyter notebook:
```docker run -it --rm -p 8888:8888 -v $PWD:/workdir -w /workdir fermi-tutorial:v1-0-0```
