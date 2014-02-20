#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte %(num_cores)d
#$ -V
#$ -l qname=%(queue)s
#$ -l h_rt=24:00:00
#$ -l h_vmem=2.875G

module load intel/ict/4.0
module load ofed/openmpi/intel/1.2.8

source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

mpirun --mca btl self,openib,sm,tcp -np $NSLOTS %(code)s %(seedname)s

echo Job ended at: `date`

