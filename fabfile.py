from fabistrano.deploy import *
from fabric.api import cd

username = raw_input('Servers Username: ')
password = raw_input('Servers Password: ')
env.user = username
env.password = password
env.hosts = ["10.123.120.196","10.123.120.197","10.123.120.198","10.123.120.199"]
env.base_dir = '/usr/local/src' # Set to your app's directory
env.app_name = 'imenu' # This will deploy the app to /www/app_name.com/
env.remote_owner = username
env.remote_group = username
env.pip_install_command = 'pip install -r requirements.txt'
env.git_clone = 'git@github.com:dpalominop/InteractiveMenu.git' # Your git url
env.restart_cmd = '' # Restart command
# or
# env.wsgi_path = "app_name/apache.wsgi" # Relative path to the wsgi file to be touched on restart

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
    db_database = raw_input('db_database: ')
    db_hostname = raw_input('db_hostname: ')
    db_username = raw_input('db_username: ')
    db_password = raw_input('db_password: ')
    sf_hostname = raw_input('sf_hostname: ')
    sf_username = raw_input('sf_username: ')
    sf_password = raw_input('sf_password: ')
    sudo_run("echo '[database]\nmotor: postgres\ndatabase: %s\nhostname: %s\nusername: %s\npassword: %s' > /etc/lssh.conf"%(db_database,
                                                                                                                             db_hostname,
                                                                                                                             db_username,
                                                                                                                             db_password)
             )
    sudo_run("echo '[fileserver]\nhostname: %s\nusername: %s\npassword: %s' >> /etc/lssh.conf"%(sf_hostname,
                                                                                                 sf_username,
                                                                                                 sf_password)
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
