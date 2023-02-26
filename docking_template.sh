#PBS -l nodes=1:ppn=4

#PBS -l walltime=96:00:00

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

module load schrodinger

module load anaconda3/2020.07

source activate /gpfs/group/cdm8/default/veda/HM_MD/pymol

python ensemble_docking.py output_ligands.maegz reference.mae NAD frames.list --jobname test_dir2 --njobs 4
