#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte 8
#$ -V
#$ -l qname=shortpara.q
#$ -l h_vmem=23.000000G

module load intel/ics-2012
module load openmpi-x86_64

source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

set MPIRUN   = mpirun
set MPIFLAGS = "--mca btl self,openib,sm,tcp"

$MPIRUN $MPIFLAGS -np 8 castep.mpi ethanol-50ry

echo Job ended at: `date`


