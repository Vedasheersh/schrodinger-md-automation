
STRUCTALIGN_CMD = '/opt/aci/sw/schrodinger/2019.4_gcc-4.8.5-zv5/utilities/structalign'
GEN_GLIDE_GRID_CMD = '/opt/aci/sw/schrodinger/2019.4_gcc-4.8.5-zv5/utilities/generate_glide_grids'

from pymol import cmd
import argparse
import pymol
import sys
pymol.finish_launching(['pymol','-qc'])

def com(selection, state=None, mass=None, object=None, quiet=1, **kwargs):
    quiet = int(quiet)
    if (object == None):
        try:
            object = cmd.get_legal_name(selection)
            object = cmd.get_unused_name(object + "_COM", 0)
        except AttributeError:
            object = 'COM'
    cmd.delete(object)

    if (state != None):
        x, y, z = get_com(selection, mass=mass, quiet=quiet)
        if not quiet:
            print("%f %f %f" % (x, y, z))
        cmd.pseudoatom(object, pos=[x, y, z], **kwargs)
        cmd.show("spheres", object)
    else:
        for i in range(cmd.count_states()):
            x, y, z = get_com(selection, mass=mass, state=i + 1, quiet=quiet)
            if not quiet:
                print("State %d:%f %f %f" % (i + 1, x, y, z))
            cmd.pseudoatom(object, pos=[x, y, z], state=i + 1, **kwargs)
            cmd.show("spheres", 'last ' + object)

cmd.extend("com", com)


def get_com(selection, state=1, mass=None, quiet=1):
    """
 DESCRIPTION

    Calculates the center of mass

    Author: Sean Law
    Michigan State University
    slaw (at) msu . edu
    """
    quiet = int(quiet)

    totmass = 0.0
    if mass != None and not quiet:
        print("Calculating mass-weighted COM")

    state = int(state)
    model = cmd.get_model(selection, state)
    x, y, z = 0, 0, 0
    for a in model.atom:
        if (mass != None):
            m = a.get_mass()
            x += a.coord[0] * m
            y += a.coord[1] * m
            z += a.coord[2] * m
            totmass += m
        else:
            x += a.coord[0]
            y += a.coord[1]
            z += a.coord[2]

    if (mass != None):
        return x / totmass, y / totmass, z / totmass
    else:
        return x / len(model.atom), y / len(model.atom), z / len(model.atom)

cmd.extend("get_com", get_com)

import os


def run(args):
    os.chdir(args.jobname)
    f = open(args.frames_list)
    frames = []
    for line in f:
        if line.strip():
            frames.append(line.strip())
    
    f = open('gridfiles2.list')
    grids = []
    for line in f:
        if line.strip():
            grids.append(line.strip())
    
    if len(grids)!=len(frames):
        print('Grid files dont exist for some frames specified in {0}. Something wrong! Bye!'.format(args.frames_list))
        sys.exit(0)
            
    print('#STEP 4 - RUN GLIDE')
    
    for gridfile,frame in zip(grids,frames):
        #write glide inp file 
        f = open('glide_00{0}.inp'.format(frame[:-6]),'w')
        f.write('GRIDFILE={0}\nLIGANDFILE={1}\n WRITE_CSV=True\nDOCKING_METHOD=confgen'.format(gridfile,args.ligand_file))
        f.close()
        
        COMMAND = 'glide glide_00{0}.inp -SAVE -NOJOBID -HOST localhost:{1}'.format(frame[:-6],args.njobs)
        
        os.system(COMMAND)
    
if __name__ == '__main__':

    # Argument parser
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    p.add_argument("ligand_file", type=str,
                   help=".maegz file containing prepared ligands")
    p.add_argument("reference_file", type=str,
                   help=".mae or .pdb file of reference structure")
    p.add_argument("reference_ligname", type=str,
                   help="Three letter residue name of ligand in refernce structure")
    p.add_argument("frames_list", type=str,
                   help="Text file containing paths to frames in .maegz or .pdb format")
    p.add_argument("--njobs",type=int,help="Number of parallel jobs to run (max=4)")
    p.add_argument("--jobname",type=str,help="Give a unique name to this job to make a directory and run simulations in there")
    
    print(p.parse_args())
    print(run(p.parse_args()))
