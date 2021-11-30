#!/bin/bash --login
set -e #o pipefail
#conda init bash
#source /root/.bashrc
#conda activate fermipy-v1-0-1
export PATH=${PATH}:/miniconda3/envs/fermipy-v1-0-1/bin
python /temp/start-env.py
#jupyter-lab --notebook-dir=/workdir --ip='0.0.0.0' --port=8888 --no-browser --allow-root
