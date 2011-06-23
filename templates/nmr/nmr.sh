#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte 64
#$ -V
#$ -l qname=parallel.q

source /home/green/pylib/castepy/templates/cluster_local.csh
source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

mpirun -np $NSLOTS castep %(seedname)s

echo Job ended at: `date`

echo "Finished $1 at `date`" | mail -s "[Kittel] MPI job finished: $1" tim.green@materials.ox.ac.uk

