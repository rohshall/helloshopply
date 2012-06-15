import sys
import time
import os
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
HOST = 'ec2-107-22-67-10.compute-1.amazonaws.com'
# set up remote environment for fabric
# DNS entry of our instance
env.hosts = [HOST]
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


def setup_packages():
  """install necessary packages"""
  sudo('wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -')
  sudo("sh -c 'echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list'")
  sudo('apt-get -y update')
  sudo('apt-get install -y python python-pycurl python-pip jenkins')
  sudo('pip install tornado pyes') # install python web server and elasticsearch client
  sudo('apt-get install -y git')
  sudo('git config --global user.name "Salil Wadnerkar"')
  sudo('git config --global user.email rohshall@gmail.com')
  sudo('ssh-keygen -C "rohshall@gmail.com" -t rsa')
  sudo('git clone git@github.com:rohshall/helloshopply.git')
  with cd('helloshopply'):
    sudo('cp shopply.conf /etc/init')
  sudo('initctl reload-configuration')


def setup_elasticsearch():
  # setup elasticsearch by downloading the server and configuring it
  sudo('wget http://github.com/downloads/elasticsearch/elasticsearch/elasticsearch-0.19.4.deb')
  # Ubuntu comes with openjdk-6-jre installation
  sudo('dpkg -i elasticsearch-0.19.4.deb')
  sudo('rm elasticsearch-0.19.4.deb')


def start_service():
  sudo('stop shopply')
  with cd('helloshopply'):
    sudo('git reset --hard')
    sudo('git pull')
  sudo('start shopply')


def check_status():
  open_shell()
  sudo('service jenkins status')
  sudo('service elasticsearch status')
  sudo('service shopply status')
  local('curl -i -H "Accept: application/json" ec2-107-22-67-10.compute-1.amazonaws.com:8888')
