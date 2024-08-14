#!/bin/bash
set -e

# Source the conda.sh script to ensure conda is initialized
source /miniconda3/etc/profile.d/conda.sh

# Check if the container is being launched into a Bash shell
if [ "$1" == "/bin/bash" ]; then
    # No need to re-source environment variables; just activate Conda
    conda activate fermipy-v1-2-2
    exec "$@"
else
    # Otherwise, assume it's being launched for Jupyter and source env variables
    source ~/.bashrc
    conda activate fermipy-v1-2-2

    # If no arguments are passed, default to starting a Jupyter notebook
    if [ $# -eq 0 ]; then
        exec jupyter notebook --notebook-dir=/workdir --ip='0.0.0.0' --port=8888 --no-browser --allow-root
    else
        # Otherwise, run the command provided (like /bin/bash)
        exec "$@"
    fi
fi

#end of entrypoint.sh file