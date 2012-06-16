import sys
import time
import os
import socket
import boto
from fabric.api import env, sudo, cd, local
from fabric.operations import get, put, open_shell

# EC2 config
AMI = 'ami-ac9943c5'
KEYPAIR = 'shopplykey'
# path to the SSH key for the EC2 instance
HOME = os.environ['HOME']
key_path = HOME + '/.ssh/shopplykey.pem'
# instance host
REMOTE_HOST = 'ec2-107-22-67-10.compute-1.amazonaws.com'
# set up remote environment for fabric
# DNS entry of our instance
env.hosts = [REMOTE_HOST]
env.user = 'ubuntu'
env.key_filename = key_path


def launch_ec2_instance():
  """launch EC2 instance using boto magic"""
  c = boto.connect_ec2()
  # get image corresponding to this AMI
  image = c.get_image(AMI)
  print 'Launching EC2 instance ...'
  # launch an instance using this image, key and security groups
  # by default this will be an m1.small instance
  res = image.run(key_name=KEYPAIR, security_groups=['default'])
  print res.instances[0].update()
  instance = None
  while True:
    print '.',
    sys.stdout.flush()
    dns = res.instances[0].dns_name
    if dns:
        instance = res.instances[0]
        break
    time.sleep(5.0)
    res.instances[0].update()
  print 'Instance started. Public DNS: ', instance.dns_name


def setup_elasticsearch():
  """setup elasticsearch by downloading the server and configuring it"""
  sudo('wget http://github.com/downloads/elasticsearch/elasticsearch/elasticsearch-0.19.4.deb')
  # Ubuntu comes with openjdk-6-jre installation
  sudo('dpkg -i elasticsearch-0.19.4.deb')
  sudo('rm elasticsearch-0.19.4.deb')


def install_packages():
  """install necessary packages"""
  # Add jenkins to the software repository
  sudo('wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -')
  sudo("sh -c 'echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list'")
  sudo('apt-get -y update')
  sudo('apt-get install -y python python-pycurl python-pip jenkins git ganglia-monitor')
  # install python web server and elasticsearch client
  sudo('pip install tornado pyes nose')


def setup_repo():
  """sets up the repo for user jenkins for the continuous integration tests"""
  sudo('git config --global user.name "jenkins ci"')
  sudo('git config --global user.email jenkins@localhost')
  sudo('ssh-keygen -C "jenkins@localhost" -t rsa')
  sudo('git clone git@github.com:rohshall/helloshopply.git')
  # Repo contains an upstart service - shopply that starts the application server (tornado server); Install it.
  with cd('helloshopply'):
    sudo('cp shopply.conf /etc/init')
    # ganglia installation needs some tweaking on Ubuntu because it did not install the python_modules that
    # we need to extend standard monitoring report
    sudo('mkdir /etc/ganglia/conf.d')
    sudo('cp modpython.conf service_monitor.pyconf /etc/ganglia/conf.d/')
    sudo('mkdir /usr/lib/ganglia/python_modules')
    sudo('cp service_monitor.py /usr/lib/ganglia/python_modules')
  sudo('initctl reload-configuration')
  sudo('service elasticsearch start')
  sudo('service ganglia-monitor start')


def start_service():
  """pull the changes from the git repository and start the service"""
  with cd('helloshopply'):
    sudo('git reset --hard')
    sudo('git pull')
  sudo('service shopply restart')


def install_web_monitoring_locally_on_ubuntu():
  """install ganglia frontend on ubuntu host; which comes with apache httpd installation"""
  local('sudo apt-get install -y gmetad ganglia-webfrontend')
  local("sudo sed -i -e 's/data_source \"my cluster\" localhost/data_source \"my cluster\" %s/g /etc/ganglia/gmetad.conf" % REMOTE_HOST)
  # copy the ganglia apache configuration to local apache server config and restart the server to make it come into effect
  local("sudo cp /etc/ganglia-webfrontend/apache.conf /etc/apache2/conf.d/ganglia.conf")
  local("sudo service gmetad restart")
  local("sudo service apache2 restart")


SERVICES = { 'jenkins': 8080, 'shopply': 8888, 'ganglia-monitor': 8649 }

def check_status():
  """check the status of all servers - elasticsearch and tornado for application and jenkins for continuous integration
  and ganglia-monitor for instance health-check. And also whether we can access these services from local host"""
  for service, port in SERVICES.iteritems():
    # check the service status on remote; except ganglia-monitor which does not support 'status' command
    if service != 'ganglia-monitor':
      sudo('service %s status' % service) 
    # check whether we can access this service from the host
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(6)
    try:
      sock.connect((REMOTE_HOST, port))
    except (socket.error, socket.timeout), e:
      print(e)
      print('service %s (port %d) is NOT active' % (service, port))
    else:
      print('service %s (port %d) is active' % (service, port))
    finally:
      sock.close()
  # elasticsearch is an internal service with no external visibility
  sudo('service elasticsearch status')
  # while we are here, run a small integration test to make sure things are alright
  local('curl -i -H "Accept: application/json" %s:%s' % (REMOTE_HOST, SERVICES['shopply']))
