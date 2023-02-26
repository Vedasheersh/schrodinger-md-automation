#PBS -l nodes=1:ppn=20

#PBS -l walltime=4:00:00

#PBS -l pmem=3gb

#PBS -l mem=3gb

#PBS -A cdm8_b_g_sc_default
#PBS -j oe

#PBS -l feature=rhel7

set -u

cd $PBS_O_WORKDIR

echo " "

echo " "

echo "JOB Started on $(hostname -s) at $(date)"

export PATH=/usr/local/cuda-10.2/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-10.2/lib64:$LD_LIBRARY_PATH

module load anaconda3/2020.07
source activate /gpfs/group/cdm8/default/veda/HM_MD/pymol

module load gcc/8.3.1
module load parallel/20190222

module load schrodinger

python analyze_md_results.py . 100ns_md-out.cms 100ns_md_trj --step {0} --output rmsds.csv

