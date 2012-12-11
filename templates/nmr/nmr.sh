#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte %(num_cores)d
#$ -V
#$ -l h_rt=2:00:00
#$ -l h_vmem=%(h_vmem)fG

source %(CASTEPY_ROOT)s/templates/cluster_local.csh
source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

mpirun -np $NSLOTS castep %(seedname)s

echo Job ended at: `date`

