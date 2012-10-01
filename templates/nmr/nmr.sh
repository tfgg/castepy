#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte 8
#$ -V
#$ -l qname=parallel.q

source /home/green/pylib/castepy/templates/cluster_local.csh
source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

mpirun -np $NSLOTS castep-jc %(seedname)s

echo Job ended at: `date`

