#!/bin/sh

#SBATCH --output=logs/job%j.log
#SBATCH --error=logs/job%j.err
#SBATCH --time=24:00:00
#SBATCH --partition=CPU
#SBATCH --cpus-per-task=48

set -x
sh PUBCHEM_download.sh