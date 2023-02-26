import os

DIRS = '''/gpfs/group/cdm8/default/veda/ctherm_auto/26_PGK
/gpfs/group/cdm8/default/veda/ctherm_auto/27_PGMT
/gpfs/group/cdm8/default/veda/ctherm_auto/28_PPDK
/gpfs/group/cdm8/default/veda/ctherm_auto/19_LDH_L
'''

DIRS = [d.strip() for d in DIRS.split('\n') if d.strip()]

STATUS_DIC = {}
f = open('status.txt','a')

maindir = os.getcwd()
i = 0
for dirpath in DIRS:
    dirname = dirpath.split('/')[-1]
    f = open(dirname+'.sh','w')
    if i%3==0:
        f.write(open('job_cdm.sh').read().format(dirpath))
        f.close()
        os.system('qsub {0}.sh'.format(dirname))
    else:
        f.write(open('job_mms.sh').read().format(dirpath))
        f.close()
        os.system('qsub {0}.sh'.format(dirname))
    i+=1
    
