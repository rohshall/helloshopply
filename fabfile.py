import sys
import time
import boto
from fabric.api import env, sudo

# EC2 config
AMI = 'ami-ac9943c5'
KEYPAIR = 'shopplykey'
# path to the SSH key for the EC2 instance
key_path = '/home/salil/.ssh/shopplykey.pem'
# instance host
HOST = 'ec2-107-22-67-10.compute-1.amazonaws.com'

def launch_ec2_instance():
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
  # DNS entry of our instance
  env.hosts = [HOST]
  env.user = 'ubuntu'
  env.key_filename = key_path

def setup_packages():
  sudo('apt-get -y update')
  sudo('apt-get install -y python python-pycurl python-pip')
  sudo('pip install tornado')
  sudo('pip install pyes')
  sudo('wget https://github.com/downloads/elasticsearch/elasticsearch/elasticsearch-0.19.4.tar.gz')
  sudo('tar -xvf elasticsearch-0.19.4.tar.gz -C /usr/local/')
  sudo('apt-get install -y openjdk-7-jre-headless')
  sudo('java -version')
  sudo('/usr/local/elasticsearch-0.19.4/bin/plugin -install elasticsearch/elasticsearch-cloud-aws/1.6.0')
