import sys
import time
import os
import boto
from fabric.api import env, sudo
from fabric.operations import put

# EC2 config
AMI = 'ami-ac9943c5'
KEYPAIR = 'shopplykey'
# path to the SSH key for the EC2 instance
HOME = os.environ['HOME']
key_path = HOME + '/.ssh/shopplykey.pem'
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
  # elasticsearch is java-based
  sudo('apt-get install -y openjdk-7-jre-headless')
  sudo('java -version')


def setup_elasticsearch():
  """Setup elasticsearch by downloading the server and configuring it"""
  sudo('curl -k -L -o elasticsearch-0.19.4.tar.gz http://github.com/downloads/elasticsearch/elasticsearch/elasticsearch-0.19.4.tar.gz')
  sudo('tar -xvf elasticsearch-0.19.4.tar.gz')
  sudo('rm elasticsearch-0.19.4.tar.gz')
  # Configure elasticsearch
  sudo('mkdir -p /etc/elasticsearch')
  # Make sure we are only listening on the localhost
  sudo("echo 'network.bind_host: 127.0.0.1' >> elasticsearch-0.19.4/config/elasticsearch.yml")
  sudo('cp elasticsearch-0.19.4/config/elasticsearch.yml /etc/elasticsearch/')
  sudo("echo -e 'gateway: DEBUG\norg.apache: WARN\ndiscovery: TRACE' >> elasticsearch-0.19.4/config/logging.yml")
  sudo('cp elasticsearch-0.19.4/config/logging.yml /etc/elasticsearch/')
  sudo('mv elasticsearch-0.19.4 /usr/local/elasticsearch')
  # Since we are going to use elasticsearch locally, no need to install the aws plugin for elasticsearch


def setup_elasticsearch_service():
  # Create the service
  put('elasticsearch', '/etc/init.d/', use_sudo=True)
  # make the init script executable 
  sudo('chmod u+x /etc/init.d/elasticsearch')
  # install the service
  sudo('update-rc.d elasticsearch defaults')
  sudo('/etc/init.d/elasticsearch start')


def current():
  pass
