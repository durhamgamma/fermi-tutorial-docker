# fermi-tutorial-docker
Docker package for fermi tutorial

## To build the image
```docker build --build-arg condaEnvFile=./tutorial-environment.yml --build-arg condaEnvName="fermipy-v1-0-1" -t fermi-tutorial:v1-0-0 .```

## To run the newly created docker container starting in the shell (Your system may require you to include a -c flag before the image name):
```docker run -it --rm -v $PWD:/workdir -w /workdir --entrypoint /bin/bash fermi-tutorial:v1-0-0```

## To run the newly created docker container starting in a Jupyter notebook:
```docker run -it --rm -p 8888:8888 -v $PWD:/workdir -w /workdir fermi-tutorial:v1-0-0```
