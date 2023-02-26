import os
import sys

SCHRODINGER_PATH = '/opt/aci/sw/schrodinger/2019.4'
SCHRODINGER_PATH2 = '/opt/aci/sw/schrodinger/2019.4_gcc-4.8.5-zv5'
SCHRODINGER_ACAD_PATH = '/gpfs/group/cdm8/default/protein_external/schrodinger2020-1'

def prepwizard(input_file, output_file, pH):
    """
    Does the default protein preparation steps at the specified pH.
    :param input_file: 'string', filepath and name for input file (.pdb or .mae)
    :param output_file: 'string', filepath and name for output file (will be output as .mae)
    :param pH: 'float'
    :return: 'int', command run status as integer (non-zero means fail, zero means success)
    """

    # Place-holders: {0} -> SCHRODINGER_PATH
    # {1} -> input_pdb
    # {2} -> pH
    command = "{0}/utilities/prepwizard {1} {2} -propka_pH {3} -fillsidechains -fillloops -HOST localhost -WAIT " \
              "-NOJOBID".format(SCHRODINGER_PATH2, input_file, output_file, pH)
    status = os.system(command)
    return status


def system_builder(input_file, output_file, salt_conc=0.15):
    """
    Build MD system in explicit solvent using Desmond system builder
    :param input_file: 'string', prepared protein .mae file
    :param output_file: 'string', name for output .cms file
    :param salt_conc: 'float', concentration for salt to add
    :return: status: 'int', non-zero means failed
    """
    
    # this msj will add Salt at specified conc., SPC solvent and OPLS_2005
    msj_file = '''
    task {
      task = "desmond:auto"
    }
    
    build_geometry {
      add_counterion = {
         ion = Na
         number = neutralize_system
      }
      box = {
         shape = orthorhombic
         size = [10.0 10.0 10.0 ]
         size_type = buffer
      }
      override_forcefield = OPLS_2005
      rezero_system = true
      salt = {
         concentration = '''+str(salt_conc)+'''
         negative_ion = Cl
         positive_ion = Na
      }
      solvent = SPC
    }
    
    assign_forcefield {
      forcefield = OPLS_2005
    }
    '''

    f = open('system.msj', 'w')
    f.write(msj_file)
    f.close()

    # Place-holders: {0} -> SCHRODINGER_PATH
    # {1} -> input_pdb
    # {2} -> pH
    command = "{0}/utilities/multisim {1} -o {2} -m system.msj -HOST localhost -WAIT".format(SCHRODINGER_PATH2,
                                                                                             input_file, output_file)
    status = os.system(command)
    return status

def system_convert(input_file,solvent_model='tip3p',forcefield='amber99SB-ILDN'):
    """
    Convert MD system to specified force-field and solvent model
    :param solvent_model: 'string', prepared protein .mae file
    :param forcefield: 'string', name for output .cms file
    :param input_file: 'string', MD system .cms file
    :param output_file: 'string', prepared protein .mae file
    :return: output: 'string'
    """
    
    # Place-holders: {0} -> SCHRODINGER_ACAD path
    # {1} -> Input CMS file
    # {2} -> Output CMS file
    # {3} -> Force-filed name
    # {4} -> Solvent model name
    
    VIPARR_CMD = '{0}/run viparr.py {1} {2} -f {3} -f {4}'
    
    # Place-holders: {0} -> Input CMS file
    # {1} -> Output CMS file
    CONS_CMD = '/gpfs/group/cdm8/default/protein_external/schrodinger2020-1/run build_constraints.py {0} {1}'

    tag = input_file[:-4]
    output_file = tag+'_amber.cms'
    status = os.system(VIPARR_CMD.format(SCHRODINGER_ACAD_PATH,input_file,output_file,forcefield,solvent_model))

    if status != 0:
        return None

    else:
        input = output
        output = tag+'_amber_cons.cms'
        status = os.system(VIPARR_CMD.format(input, output))

        
        if status !=0:
            return None
        else:
            return output_file

def md(input_file, temperature, time=100000):
    """

    :param input_file:
    :param temperature:
    :param time:
    :return:
    """

    msj_file = '''
    # Desmond standard NPT relaxation protocol
    # All times are in the unit of ps.
    # Energy is in the unit of kcal/mol.
    task {
       task = "desmond:auto"
       set_family = {
          desmond = {
             checkpt.write_last_step = no
          }
       }
    }
    
    simulate {
       title       = "Brownian Dynamics NVT, T = 10 K, small timesteps, and restraints on solute heavy atoms, 100ps"
       annealing   = off
       time        = 100
       timestep    = [0.001 0.001 0.003 ]
       temperature = 10.0
       ensemble = {
          class = "NVT"
          method = "Brownie"
          brownie = {
             delta_max = 0.1
          }
       }
       restrain = {
          atom = "solute_heavy_atom"
          force_constant = 50.0
       }
    }
    
    simulate {
       effect_if   = [["==" "-gpu" "@*.*.jlaunch_opt[-1]"] 'ensemble.method = Langevin']
       title       = "NVT, T = 10 K, small timesteps, and restraints on solute heavy atoms, 12ps"
       annealing   = off
       time        = 12
       timestep    = [0.001 0.001 0.003]
       temperature = 10.0
       restrain    = { atom = solute_heavy_atom force_constant = 50.0 }
       ensemble    = {
          class  = NVT
          method = Berendsen
          thermostat.tau = 0.1
       }
    
       randomize_velocity.interval = 1.0
       eneseq.interval             = 0.3
       trajectory.center           = []
    }
    
    simulate {
       title       = "NPT, T = 10 K, and restraints on solute heavy atoms, 12ps"
       effect_if   = [["==" "-gpu" "@*.*.jlaunch_opt[-1]"] 'ensemble.method = Langevin']
       annealing   = off
       time        = 12
       temperature = 10.0
       restrain    = retain
       ensemble    = {
          class  = NPT
          method = Berendsen
          thermostat.tau = 0.1
          barostat  .tau = 50.0
       }
    
       randomize_velocity.interval = 1.0
       eneseq.interval             = 0.3
       trajectory.center           = []
    }
    
    solvate_pocket {
       should_skip = true
       ligand_file = ?
    }
    
    simulate {
       title       = "NPT and restraints on solute heavy atoms, 12ps"
       effect_if   = [["@*.*.annealing"] 'annealing = off temperature = "@*.*.temperature[0][0]"'
                      ["==" "-gpu" "@*.*.jlaunch_opt[-1]"] 'ensemble.method = Langevin']
       time        = 12
       restrain    = retain
       ensemble    = {
          class  = NPT
          method = Berendsen
          thermostat.tau = 0.1
          barostat  .tau = 50.0
       }
    
       randomize_velocity.interval = 1.0
       eneseq.interval             = 0.3
       trajectory.center           = []
    }
    
    simulate {
       title       = "NPT and no restraints, 24ps"
       effect_if   = [["@*.*.annealing"] 'annealing = off temperature = "@*.*.temperature[0][0]"'
                      ["==" "-gpu" "@*.*.jlaunch_opt[-1]"] 'ensemble.method = Langevin']
       time        = 24
       ensemble    = {
          class  = NPT
          method = Berendsen
          thermostat.tau = 0.1
          barostat  .tau = 2.0
       }
    
       eneseq.interval   = 0.3
       trajectory.center = solute
    }
    
    simulate {
       cfg_file = "md.cfg"
       jobname  = "$MASTERJOBNAME"
       dir      = "."
       compress = ""
    }
    '''

    cfg_file = '''
    annealing = false
    backend = {
    }
    bigger_rclone = false
    checkpt = {
       first = 0.0
       interval = 240.06
       name = "$JOBNAME.cpt"
       write_last_step = true
    }
    cpu = 1
    cutoff_radius = 9.0
    elapsed_time = 0.0
    energy_group = false
    eneseq = {
       first = 0.0
       interval = 1.2
       name = "$JOBNAME$[_replica$REPLICA$].ene"
    }
    ensemble = {
       barostat = {
          tau = 2.0
       }
       class = NPT
       method = MTK
       thermostat = {
          tau = 1.0
       }
    }
    glue = solute
    maeff_output = {
       first = 0.0
       interval = 120.0
       name = "$JOBNAME$[_replica$REPLICA$]-out.cms"
       periodicfix = true
       trjdir = "$JOBNAME$[_replica$REPLICA$]_trj"
    }
    meta = false
    meta_file = ?
    pressure = [1.01325 isotropic ]
    randomize_velocity = {
       first = 0.0
       interval = inf
       seed = 2007
       temperature = "@*.temperature"
    }
    restrain = none
    simbox = {
       first = 0.0
       interval = 1.2
       name = "$JOBNAME$[_replica$REPLICA$]_simbox.dat"
    }
    surface_tension = 0.0
    taper = false
    temperature = [
       [''' + str(temperature) + ''' 0 ]
    ]
    time = ''' + str(time) + '''
    timestep = [0.002 0.002 0.006 ]
    trajectory = {
       center = []
       first = 0.0
       format = dtr
       frames_per_file = 250
       interval = 100.0
       name = "$JOBNAME$[_replica$REPLICA$]_trj"
       periodicfix = true
       write_velocity = false
    } '''

    f = open('md.msj', 'w')
    f.write(msj_file)
    f.close()

    f = open('md.cfg', 'w')
    f.write(cfg_file)
    f.close()

    # Place-holders: {0} -> SCHRODINGER_PATH
    # {1} -> input_pdb
    # {2} -> pH
    command = '''{0}/utilities/multisim {1} -o 100ns_md-out.cms -m system.msj -HOST localhost \
    -JOBNAME 100ns_md -HOST localhost -maxjob 1 -cpu 1 -m md.msj -c md.cfg -description "Molecular Dynamics" \
    -mode umbrella -lic DESMOND_ACADEMIC:16 -WAIT''' \
        .format(SCHRODINGER_ACAD_PATH, input_file)

    status = os.system(command)
    return status

def run(dirpath):

    STATUS_DIC = ''
    # first change directory
    os.chdir(dirpath)

    # get dir name from path
    dirname = dirpath.split('/')[-1]

    # verify the presence of model
    model = dirname+'_trmodel.pdb'

    try:
        f = open(model)
    except IOError:
        STATUS_DIC = 'Read model FAILED'
        return STATUS_DIC

    # now do the steps
    status = prepwizard(model, 'prepwizard.mae', pH=7.0)
    if status!=0:
        STATUS_DIC = "Prepwizard FAILED"
        return STATUS_DIC
    status = system_builder('prepwizard.mae', 'system.cms')
    if status!=0:
        STATUS_DIC = "System builder FAILED"
        return STATUS_DIC
    #newsystem = system_convert('system.cms')
    #if newsystem==None:
        #STATUS_DIC = "Viparr FAILED"
        #return STATUS_DIC
    status = md('system.cms', 328, time=100000)
    if status!=0:
        STATUS_DIC = "MD FAILED"
        return STATUS_DIC

    return "SUCCESS"
  

if __name__ == '__main__':
    args = sys.argv
    print(run(args[1]))



