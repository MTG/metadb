from fabric.api import local
from fabric.colors import green
import os

def git_pull():
    local("git pull origin")
    print(green("Updated local code.", bold=True))


def install_requirements():
    local("pip install -r requirements.txt")
    print(green("Installed requirements.", bold=True))


def deploy():
    git_pull()
    install_requirements()

