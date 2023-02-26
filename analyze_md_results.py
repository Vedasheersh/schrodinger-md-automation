import os
import sys
import argparse
from multiprocessing import Pool
import json

SCHRODINGER_PATH = '/opt/aci/sw/schrodinger/2019.4_gcc-4.8.5-zv5'
SCHRODINGER_ACAD_PATH = '/gpfs/group/cdm8/default/protein_external/schrodinger2020-1'

def rmsd_command(i,path,step):
    COMMAND = '{0}/run rmsd.py frames_step{1}_0.maegz frames_step{1}_{2}.maegz > rmsd_step{1}_0_{2}.txt'.format(path,step,i)
    return 'rmsd_step{1}_0_{2}.txt'.format(path,step,i), COMMAND
    
def run(args):
    # first change directory
    os.chdir(args.md_directory)

    print('#STEP 1 - ALIGNING FRAMES')

    COMMAND = '{0}/run trj_align.py {1} {2} protein_aligned -s 0:-1:{3} -ref-frame 0 -asl "protein"'.format(SCHRODINGER_PATH,args.cms,args.trj,args.step)

    os.system(COMMAND)

    print('#STEP 2 - EXTRACTING FRAMES')

    COMMAND = '{0}/run trj2mae.py protein_aligned-out.cms protein_aligned_trj frames_step{1} -s 0:-1:{1} -extract-asl "protein" -out-format MAE -separate'.format(SCHRODINGER_PATH,args.step)

    os.system(COMMAND)
    os.system('ls frames_step{0}*maegz | wc -l > count'.format(args.step))
    frame_count = int(open('count').read().strip())

    print('#STEP 3 - COMPUTE RMSD')
    
    rmsd_commands = []
    rmsd_files = {}
    rmsds = {}
    
    for i in range(frame_count):
        file,command = rmsd_command(i,SCHRODINGER_PATH,args.step)
        rmsd_commands.append(command)
        rmsd_files[i] = file
    
    f = open('rmsd_commands.txt','w')
    for command in rmsd_commands:
        f.write(command+'\n')
    f.close()
    
    # run using gnu parallel
    status = os.system('parallel < rmsd_commands.txt')
    
    print(status)
    if status==0:
        for i in rmsd_files:
            temp = open(rmsd_files[i]).read()
            a,b = temp.split('In-place RMSD =')
            rmsd = float(b.split(';')[0].strip())
            print(rmsd)
            rmsds[i] = rmsd
    
    f = open(args.output,'w')
    for i in rmsds:
        f.write('{0},{1}\n'.format(i,rmsds[i]))
    f.close()
    
    return rmsds

if __name__ == '__main__':

    # Argument parser
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    p.add_argument("md_directory", type=str,
                   help="Directory containing MD results")
    p.add_argument("cms", type=str,
                   help="Name of the -out.cms file")
    p.add_argument("trj", type=str,
                   help="Name of the trj directory")
    p.add_argument("--step", type=int,default=1,
                   help="Time step for performing analysis. Default=1, takes all frames for analysis")
    p.add_argument("--output", type=str,
                   help="Output csv file name to store rmsds")
    
    print(p.parse_args())
    print(run(p.parse_args()))



