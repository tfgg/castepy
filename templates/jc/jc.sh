#!/bin/tcsh
#$ -cwd
#$ -j y
#$ -pe orte %(num_cores)d
#$ -V
#$ -l qname=%(queue)s
#$ -l h_vmem=%(h_vmem)fG

source %(CASTEPY_ROOT)s/templates/cluster_local.csh
source /opt/gridengine/default/common/settings.csh

echo Job using the following number of cores: $NSLOTS
echo Job starting on: `date`

#echo $TMPDIR/machines
#cat $TMPDIR/machines
ls $TMPDIR

mpirun --mca btl self,openib,sm,tcp -np $NSLOTS castep-jc %(seedname)s

echo Job ended at: `date`

echo "Finished $1 at `date`" | mail -s "JC MPI job finished: $1" %(USER_EMAIL)s

