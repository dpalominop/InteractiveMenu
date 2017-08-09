from fabistrano.deploy import *
from fabric.api import cd

username = raw_input('Servers Username:')
password = raw_input('Servers Password:')
env.user = username
env.password = password
env.hosts = ["10.123.120.196","10.123.120.197","10.123.120.198","10.123.120.199"]
env.base_dir = '/usr/local/src' # Set to your app's directory
env.app_name = 'imenu' # This will deploy the app to /www/app_name.com/
env.remote_owner = username
env.remote_group = username
env.pip_install_command = 'pip install -r requirements'
env.git_clone = 'git@github.com:dpalominop/InteractiveMenu.git' # Your git url
env.restart_cmd = '' # Restart command
# or
# env.wsgi_path = "app_name/apache.wsgi" # Relative path to the wsgi file to be touched on restart

@task
@with_defaults
def update_sshd_config():
    """Update file /etc/ssh/sshd_config on all servers"""
    with cd("%s/%s/current"%(env.base_dir, env.app_name)):
        sudo_run("echo 'Match User *,!root\n\tForceCommand %s/%s/current/src/menu.py' >> /etc/ssh/sshd_config"%(env.base_dir, env.app_name))
        sudo_run("service sshd restart")