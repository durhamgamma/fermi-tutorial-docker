#!/bin/bash
set -e

# Source the bashrc to ensure all environment variables are loaded
source ~/.bashrc

# Set the PFILES environment variable if not already set
export PFILES=".:/root/pfiles;/miniconda3/envs/fermipy-v1-2-2/share/fermitools/syspfiles"

# Activate the conda environment
source activate $condaEnvName

# If no arguments are passed, default to starting a Jupyter notebook
if [ $# -eq 0 ]; then
    exec jupyter notebook --notebook-dir=/workdir --ip='0.0.0.0' --port=8888 --no-browser --allow-root
else
    # Otherwise, run the command provided (like /bin/bash)
    exec "$@"
fi


# #!/bin/bash --login
# set -e #o pipefail
# #conda init bash
# #source /root/.bashrc
# #conda activate fermipy-v1-0-1
# export PATH=${PATH}:/miniconda3/envs/fermipy-v1-2-2/bin
# python /temp/start-env.py
# #jupyter-lab --notebook-dir=/workdir --ip='0.0.0.0' --port=8888 --no-browser --allow-root
