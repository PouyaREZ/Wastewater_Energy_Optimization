#!/bin/bash
#SBATCH --job-name=RQ1_W_CWWTP_ModConsts
#SBATCH --output=RQ1_W_CWWTP_ModConsts.%j.out
#SBATCH --error=RQ1_W_CWWTP_ModConsts.%j.err
#SBATCH --time=0-3:00:00
#SBATCH -p cee
#SBATCH -c 10
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=pouyar@stanford.edu
module load python/3.6.1
python3 -m scoop --host $HOSTNAME -vv -n 10 SF_CaseStudy_Ch1_Pouya.py
