from fabistrano.deploy import *

username = raw_input('Servers Username:')
password = raw_input('Servers Password:')
env.user = username
env.password = password
env.hosts = ["10.123.120.196","10.123.120.197","10.123.120.198","10.123.120.199"]
env.base_dir = '/usr/local/src' # Set to your app's directory
env.app_name = 'imenu' # This will deploy the app to /www/app_name.com/
env.remote_owner = username
env.remote_group = username
env.pip_install_command = ''
env.git_clone = 'git@github.com:dpalominop/InteractiveMenu.git' # Your git url
env.restart_cmd = '' # Restart command
# or
# env.wsgi_path = "app_name/apache.wsgi" # Relative path to the wsgi file to be touched on restart
