#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte 16
#$ -V
#$ -l qname=parallel.q
#$ -l h_vmem=46G

source %(CASTEPY_ROOT)s/templates/cluster_local.csh
source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

#echo $TMPDIR/machines
#cat $TMPDIR/machines
ls $TMPDIR

mpirun -np $NSLOTS castep-jc %(seedname)s

echo Job ended at: `date`

echo "Finished $1 at `date`" | mail -s "JC MPI job finished: $1" %(USER_EMAIL)s

