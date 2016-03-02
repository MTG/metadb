from fabric.api import local
from fabric.colors import green
import os

def git_pull():
    local("git pull origin")
    print(green("Updated local code.", bold=True))


def install_requirements():
    local("pip install -r requirements.txt")
    print(green("Installed requirements.", bold=True))


def vssh():
    """SSH to a running vagrant host."""
    curdir = os.path.dirname(os.path.abspath(__file__))
    configfile = os.path.join(curdir, '.vagrant', 'ssh_config')
    if not os.path.exists(configfile):
        local('vagrant ssh-config metadb > .vagrant/ssh_config')

    local("ssh -F .vagrant/ssh_config -o 'ControlMaster auto' -o 'ControlPath ~/.ssh/mdb_vagrant_control' -o 'ControlPersist 4h' metadb")


def deploy():
    git_pull()
    install_requirements()
