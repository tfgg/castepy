#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte %(num_round_cores)d
#$ -V
#$ -l qname=%(queue)s
#$ -l h_vmem=%(h_vmem)fG

module load intel/ics-2012
module load openmpi-x86_64

source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

set MPIRUN   = mpirun
set MPIFLAGS = --mca btl self,openib,sm,tcp

$MPIRUN $MPIFLAGS -np %(num_cores)d %(code)s %(seedname)s

echo Job ended at: `date`

