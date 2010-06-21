from fabric.api import *

env.hosts = ['razor']
repo = '/home/pat/src/ffo'

def deploy(commit=None):
    if commit is None:
        git_pull()
    else:
        git_reset_hard(commit)
    restart_servers()

def git_pull():
    with cd(repo):
        run('git pull')

def git_reset_hard(commit):
    with cd(repo):
        run('git reset --hard %s' % commit)

def restart_servers():
    for p in (8200, 8201, 8202, 8203):
        sudo('supervisorctl restart ffo-%d' % p)
