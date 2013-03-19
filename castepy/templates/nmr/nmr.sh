#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte %(num_cores)d
#$ -V
#$ -l qname=parallel.q
#$ -l h_vmem=%(h_vmem)fG

source %(CASTEPY_ROOT)s/templates/cluster_local.csh
source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

mpirun --mca btl self,openib,sm,tcp -np $NSLOTS castep %(seedname)s

echo Job ended at: `date`

