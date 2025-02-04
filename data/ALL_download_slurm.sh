#!/bin/sh

#SBATCH --output=logs/job%j.log
#SBATCH --error=logs/job%j.err
#SBATCH --time=24:00:00
#SBATCH --partition=CPU
#SBATCH --cpus-per-task=100

set -x
sh BACE_download.sh
sh ESOL_download.sh
sh HIV_download.sh
sh PCBA_download.sh
sh PUBCHEM_download.sh
Sh QM9_download.sh
sh QM4D_download.sh
sh TOX21_download.sh
sh ZINC1M_download.sh
sh ZINC10M_download.sh
sh ZINC25k_download.sh
sh ALCHEMY_download.sh