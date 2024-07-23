#!/bin/bash

TARGETPLATFORM=$1

case "${TARGETPLATFORM}" in
  "linux/amd64")
    MINIFORGE_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"
    ;;
  "linux/arm64")
    MINIFORGE_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh"
    ;;
  "darwin/amd64")
    MINIFORGE_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh"
    ;;
  "darwin/arm64")
    MINIFORGE_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh"
    ;;
  *)
    echo "Unsupported platform: ${TARGETPLATFORM}"
    exit 1
    ;;
esac

curl -L -O "${MINIFORGE_URL}"
bash $(basename "${MINIFORGE_URL}")