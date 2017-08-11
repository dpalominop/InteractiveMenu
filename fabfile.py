from fabistrano.deploy import *
from fabric.api import cd

"""create file .fabricrc with arguments:
user = ''
password = ''
remote_owner = ''
remote_group = ''
base_dir = ''
app_name = ''
env.restart_cmd = ''

db_database = ''
db_hostname = ''
db_username = ''
db_password = ''
sf_hostname = ''
sf_username = ''
sf_password = ''
And execute: fab -c .fabricrc my_task"""

env.hosts = ['10.123.120.196', '10.123.120.197', '10.123.120.198', '10.123.120.199']
env.pip_install_command = 'pip install -r requirements.txt'
env.git_clone = 'git@github.com:dpalominop/InteractiveMenu.git'

@task
@with_defaults
def update_sshd_config():
    """Update file /etc/ssh/sshd_config on all servers"""
    sudo_run("echo 'Match User *,!root\n\tForceCommand %s/%s/current/src/menu.py' >> /etc/ssh/sshd_config"%(env.base_dir, env.app_name))
    sudo_run("service sshd restart")

@task
@with_defaults
def update_ssh_config():
    """Update file /etc/ssh/ssh_config on all servers"""
    sudo_run("echo 'StrictHostKeyChecking no\nUserKnownHostsFile /dev/null\nLogLevel ERROR' >> /etc/ssh/ssh_config"%(env.base_dir, env.app_name))

@task
@with_defaults
def update_lssh_conf():
    """Update file /etc/lssh.conf on all servers"""

    sudo_run("echo '[database]\nmotor: postgres\ndatabase: %s\nhostname: %s\nusername: %s\npassword: %s' > /etc/lssh.conf"%(env.db_database,
                                                                                                                             env.db_hostname,
                                                                                                                             env.db_username,
                                                                                                                             env.db_password)
             )
    sudo_run("echo '[fileserver]\nhostname: %s\nusername: %s\npassword: %s' >> /etc/lssh.conf"%(env.sf_hostname,
                                                                                                 env.sf_username,
                                                                                                 env.sf_password)
             )

@task
@with_defaults
def yum_update():
    """Execute 'yum update' in all servers"""
    sudo_run("yum update -y")

@task
@with_defaults
def reboot():
    """Execute 'reboot' atfer 5 seconds in all servers"""
    sudo_run("( sleep 5 ; reboot ) &")
