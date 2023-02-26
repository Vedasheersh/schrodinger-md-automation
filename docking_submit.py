import os
import time
import subprocess
import sys
import argparse

# Argument parser
p = argparse.ArgumentParser(description=__doc__,
formatter_class=argparse.RawDescriptionHelpFormatter)

p.add_argument("root_directory", type=str,
           help="Directory containing directories of homology models")

args = p.parse_args()

dirpath = args.root_directory
if dirpath.endswith('/'):
    dirpath = dirpath[:-1]

os.chdir(dirpath)

# There are several directories here each of which corresponds to one model
dirs = os.listdir('.')

maindir = os.getcwd()
i = 0

print('#'*100)
print('Found {0} directories in {1}'.format(len(dirs),maindir))
print('MD jobs will be submitted for each of these sequentially')
print('#'*100)

for dirname in dirs:
    print('#'*100)
    print('Now processing {0}'.format(dirname))
    
    os.chdir(dirname)
    #Copy the code
    os.system('cp ../../ensemble_docking.py .')
    
    # Do this in two steps
    # STEP 1. Preparation
    jobname = 'docking_'+dirname+'.sh'
    f = open(jobname,'w')
    f.write(open('../docking_template.sh').read().format(dirname))
    f.close()
    
    cmd = 'qsub {0}'.format(jobname)
    os.system(cmd)

    print('Submitted docking job for {0}.. Waiting for it to finish.'.format(dirname))

    # Only once this is complete, submit MD job
    i = 0
    status = 1
    while status!=0:
        status = os.system('ls ./{0}/system.cms'.format(dirname))
        time.sleep(180)
        i+=1
        print('STAGE 1: Time elapsed: {0} minutes'.format(i*3))
    
    print('STAGE 1: Complete.')
    print('#'*100)
    
    # STEP 2. MD
    jobname = 'MD_'+dirname+'.sh'
    f = open(jobname,'w')
    f.write(open('../MD_template_cdm.sh').read().format(dirname))
    f.close()
    
    cmd = 'qsub {0}'.format(jobname)
    status = os.system(cmd)
    if status==0:
        print('STAGE 2: Submitted MD job. Check status in Job submission queue')
        print('Exiting')
        print('#'*100)
    else:
        print('STAGE 2: Could not submit MD job. Something wrong. Check job output in {0} for details'.format(maindir))
    i+=1
    os.chdir(maindir)
    
