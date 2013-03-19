#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte 32
#$ -V
#$ -l qname=parallel.q

source /home/green/pylib/castepy/templates/cluster_local.csh
source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

#echo $TMPDIR/machines
#cat $TMPDIR/machines
ls $TMPDIR

mpirun -np $NSLOTS castep $1

echo Job ended at: `date`

echo "Finished $1 at `date`" | mail -s "[Kittel] MPI job finished: $1" tim.green@materials.ox.ac.uk

