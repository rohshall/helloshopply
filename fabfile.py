import sys
import time
import boto

AMI = 'ami-ac9943c5'
KEYPAIR = 'shopplykey'

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
