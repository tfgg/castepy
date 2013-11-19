#!/usr/bin/env python
import os
from distutils.core import setup

def relative_find(start_dir, dir=""):
    files = []
    for f in os.listdir(os.path.join(start_dir, dir)):
      if os.path.isdir(os.path.join(start_dir, dir, f)):
        files = files + relative_find(start_dir, os.path.join(dir, f))
      elif not f.endswith('.pyc'):
        files.append(os.path.join(dir, f))
    return files

def recursive_find(dir):
  files = []
  for f in os.listdir(dir):
    if os.path.isdir(os.path.join(dir, f)):
      files = files + recursive_find(os.path.join(dir, f))
    elif not f.endswith('.pyc'):
      files.append(os.path.join(dir, f))
  return files

def data_files(dir):
  files = recursive_find(dir)

  data_files = []
  for f in files:
    dir, file = os.path.split(f)
    data_files.append((dir, [f]))

  return data_files
  
setup(name='Castepy',
      version='0.9',
      description='Helper scripts for using and processing Castep jobs, particularly magnetic resonance',
      author='Timothy Green',
      author_email='timothy.green@gmail.com',
      url='',
      packages=['castepy','castepy.input', 'castepy.output'],
      package_data={'castepy': relative_find('castepy', 'templates'),},
      scripts=[os.path.join('scripts', f) for f in os.listdir('scripts')],
      )

