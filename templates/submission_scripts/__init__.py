import os.path

import castepy.settings as settings


PATH, _ = os.path.split(os.path.realpath(__file__))

def getfile(p):
  return open(os.path.join(PATH, p)).read()

sub_map = {'ironman': getfile('ironman.sh'),
           'kittel': getfile('kittel.sh'),
           'hector': getfile('hector.pbs'),}

def get_submission_script():
  return sub_map[settings.PLATFORM]
