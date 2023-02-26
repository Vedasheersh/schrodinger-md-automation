#PBS -l nodes=1:ppn=2:gpus=1:shared

#PBS -l walltime=48:00:00

#PBS -l pmem=2gb

#PBS -l mem=2gb

#PBS -A cdm8_h_g_gc_default
#PBS -j oe

#PBS -l feature=rhel7

set -u

cd $PBS_O_WORKDIR

echo " "

echo " "

echo "JOB Started on $(hostname -s) at $(date)"

export PATH=/usr/local/cuda-10.2/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-10.2/lib64:$LD_LIBRARY_PATH

module load schrodinger
python schrodinger_automate-2.py {0}

