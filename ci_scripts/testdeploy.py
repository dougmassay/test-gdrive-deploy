#!/usr/bin/env python3

import os
import sys
import subprocess
import datetime
import shutil
import glob

gparent = os.path.expandvars('$GDRIVE_DIR')
grefresh_token = os.path.expandvars('$GDRIVE_REFRESH_TOKEN')
test_secure = os.path.expandvars('$MY_SECURE_TEST')

if sys.platform.lower().startswith('darwin'):
    travis_branch = os.path.expandvars('$TRAVIS_BRANCH')
    travis_commit = os.path.expandvars('$TRAVIS_COMMIT')
    travis_build_number = os.path.expandvars('$TRAVIS_BUILD_NUMBER')
    
    origfilename = './bin/Sigil.tar.xz'
    newfilename = './bin/Sigil-{}-{}-build_num-{}.tar.xz'.format(travis_branch, travis_commit[:7],travis_build_number)
else:
    appveyor_branch = os.path.expandvars('$APPVEYOR_REPO_BRANCH')
    appveyor_commit = os.path.expandvars('$APPVEYOR_REPO_COMMIT')
    appveyor_build_number = os.path.expandvars('$APPVEYOR_BUILD_VERSION')
    print('Current directory {}'.format(os.getcwd()))
    print('Script directory {}'.format(os.path.dirname(os.path.realpath(__file__))))
    print('secure var {}'.format(test_secure))
    names = glob.glob('.\\installer\\Sigil-*-Setup.exe')
    print('files {}'.format(names))
    if not names:
        exit(1)
    origfilename = names[0]
    newfilename = '.\\installer\\Sigil-{}-{}-build_num-{}-Setup.exe'.format(appveyor_branch, appveyor_commit[:7], appveyor_build_number)

print('orgifilename: {} newfilename: {}'.format(origfilename, newfilename))
shutil.copy2(origfilename, newfilename)

folder_name = datetime.date.today()
list_command = ['gdrive',
          '--refresh-token',
          '{}'.format(grefresh_token),
          'list',
          '--no-header',
          '--query',
          'trashed = false and mimeType = \'application/vnd.google-apps.folder\' and \'{}\' in parents and name = \'{}\''.format(gparent, folder_name),
         ]

list_proc = subprocess.run(list_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
print('here!')
print('{}'.format(list_proc.returncode))
if list_proc.returncode == 0 and len(list_proc.stdout):
    gparent = list_proc.stdout.split()[0]
    print('here2!')
else:
    print('here3!')
    print(list_proc.stderr)
    mk_command = ['gdrive',
                  '--refresh-token',
                  '{}'.format(grefresh_token),
                  'mkdir',
                  '--parent',
                  '{}'.format(gparent),
                  '{}'.format(folder_name),
                  ]

    mk_proc = subprocess.run(mk_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    print('{}'.format(mk_proc.returncode))
    if mk_proc.returncode == 0 and mk_proc.stdout.strip():
        print('here4!')
        print('Created new \'{}\' folder'.format(folder_name))
        gparent = mk_proc.stdout.split()[1]
print('here5!')
up_command = ['gdrive',
              '--refresh-token',
              '{}'.format(grefresh_token),
              'upload',
              '--parent',
              '{}'.format(gparent),
              '{}'.format(newfilename)
              ]
up_proc = subprocess.run(up_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
print('here6!')
info = None
if up_proc.returncode == 0:
    print('Uploaded {} to \'{}\' folder'.format(newfilename, folder_name))
    info = up_proc.stdout.splitlines()[1].split()[1]

if info is not None:
    inf_command = ['gdrive',
                   '--refresh-token',
                  '{}'.format(grefresh_token),
                  'info',
                  '{}'.format(info),
                   ]
    inf_proc = subprocess.run(inf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if inf_proc.returncode == 0:
        inf_dic = {k.split(':')[0].strip():k.split(': ')[1] for k in inf_proc.stdout.splitlines()}
        print('Download {} from {}'.format(newfilename, inf_dic["DownloadUrl"]))
else:
    exit(1)

