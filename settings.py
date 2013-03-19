import os

CASTEPY_ROOT, _ = os.path.split(os.path.realpath(__file__))

USER_EMAIL = "tim.green@materials.ox.ac.uk"

PLATFORM = "hector"

cluster_pspot_dir = {'hector': "/home/e89/e89/green/work/ncp_pspot",
                     'ironman': "/home/green/scratch/ncp_pspot",
                     'kittel': "/home/green/scratch/ncp_pspot",}

cluster_pspot_lda_dir = {'hector': "/home/e89/e89/green/work/ncp_pspot",
                         'ironman': "/home/green/scratch/ncp_pspot",
                         'kittel': "/home/green/scratch/ncp_pspot",}

NCP_PSPOT_DIR = cluster_pspot_dir[PLATFORM]

