#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte 64
#$ -V
#$ -l qname=parallel.q

module load ofed/openmpi/intel/1.2.8

source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

#echo $TMPDIR/machines
#cat $TMPDIR/machines
ls $TMPDIR

mpirun -np $NSLOTS /home/green/jc-mpi-CASTEP-5.5/obj/linux_x86_64_ifort11/castep $1

echo Job ended at: `date`

echo "Finished $1 at `date`" | mail -s "[Kittel] MPI job finished: $1" tim.green@materials.ox.ac.uk

