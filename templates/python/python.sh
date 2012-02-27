#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte %(num_nodes)d
#$ -V
#$ -l qname=parallel.q

source %(CASTEPY_ROOT)s/templates/cluster_local.csh
source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

#echo $TMPDIR/machines
#cat $TMPDIR/machines
ls $TMPDIR

mpiexec -n $NSLOTS python %(scriptname)s

echo Job ended at: `date`

