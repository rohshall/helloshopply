import sys
import time
import boto
from fabric.api import env, sudo
from fabric.operations import put

# EC2 config
AMI = 'ami-ac9943c5'
KEYPAIR = 'shopplykey'
# path to the SSH key for the EC2 instance
key_path = '/home/salil/.ssh/shopplykey.pem'
# instance host
HOST = 'ec2-107-22-67-10.compute-1.amazonaws.com'


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


def live():
  """set up remote environment for fabric""" 
  # DNS entry of our instance
  env.hosts = [HOST]
  env.user = 'ubuntu'
  env.key_filename = key_path


def setup_packages():
  """install necessary packages"""
  sudo('apt-get -y update')
  sudo('apt-get install -y python python-pycurl python-pip')
  sudo('pip install tornado') # python web server
  sudo('pip install pyes') # python elasticsearch client


def setup_elasticsearch():
  """Setup elasticsearch by downloading the server and configuring it"""
  sudo('wget https://github.com/downloads/elasticsearch/elasticsearch/elasticsearch-0.19.4.tar.gz')
  sudo('tar -xvf elasticsearch-0.19.4.tar.gz -C /usr/local/')
  sudo('mv /usr/local/elasticsearch-0.19.4 /usr/local/elasticsearch')
  # elasticsearch is java-based
  sudo('apt-get install -y openjdk-7-jre-headless')
  sudo('java -version')
  # install the aws plugin for elasticsearch
  sudo('/usr/local/elasticsearch/bin/plugin -install elasticsearch/elasticsearch-cloud-aws/1.6.0')
  put('elasticsearch.yml', '/usr/local/elasticsearch/config/', use_sudo=True)
  put('logging.yml', '/usr/local/elasticsearch/config/', use_sudo=True)
  sudo('/usr/local/elasticsearch/bin/elasticsearch -f')

def current():
  pass
