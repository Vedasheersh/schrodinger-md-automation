import os
import time
import subprocess
import sys
import argparse

# Argument parser
p = argparse.ArgumentParser(description=__doc__,
formatter_class=argparse.RawDescriptionHelpFormatter)

p.add_argument("root_directory", type=str,
           help="Directory containing directories of MD simulations")

args = p.parse_args()

dirpath = args.root_directory
if dirpath.endswith('/'):
    dirpath = dirpath[:-1]

os.chdir(dirpath)

# There are several directories here each of which corresponds to one model
dirs = os.listdir('.')

maindir = os.getcwd()
i = 0

try:
	step = int(input('Enter step for analysis:'))
except ValueError:
	print('Step should be integer, try again!')
	sys.exit(0)


print('#'*100)
print('Found {0} directories in {1}'.format(len(dirs),maindir))
print('Analysis jobs will be submitted for each of these sequentially')
print('#'*100)

for dirname in dirs:
    print('#'*100)
    print('Now processing {0}'.format(dirname))
    
    os.chdir(dirname)
    #Copy the code
    os.system('cp ../../analyze_md_results.py .')
    
    # Do this in two steps
    # STEP 1. Preparation
    jobname = 'analyze_'+dirname+'.sh'
    f = open(jobname,'w')
    f.write(open('../../analyze_template.sh').read().format(step))
    f.close()
    
    cmd = 'qsub {0}'.format(jobname)
    os.system(cmd)

    print('Submitted analysis job for {0}'.format(dirname))

    i+=1
    os.chdir(maindir)
    
