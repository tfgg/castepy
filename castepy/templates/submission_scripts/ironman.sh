#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte %(num_cores)d
#$ -V
#$ -l qname=%(queue)s
#$ -l h_vmem=%(h_vmem)fG

module load intel/ics-2012
module load openmpi-x86_64

source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

mpirun --mca btl self,openib,sm,tcp -np $NSLOTS %(code)s %(seedname)s

echo Job ended at: `date`

