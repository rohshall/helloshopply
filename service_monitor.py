import socket


descriptors = []


port_map = {'ShopplyService': 8888, 'JenkinsService': 8080}


def get_service_status(service_name):
  '''Return the service status.'''
  port = port_map[service_name]
  # check whether we can access this service from the host
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.settimeout(4)
  try:
    sock.connect(('localhost', port))
  except (socket.error, socket.timeout), e:
    return 0
  else:
    return 1
  finally:
    sock.close()


def metric_init(params):
  '''create the metric definition dictionary object for each metric.'''
  global descriptors
  print '[PyProcessMonitor] Received the following parameters: %s' % params
  port_map.update((key, int(val)) for (key, val) in params.iteritems())
  d1 = {'name': 'ShopplyService',
      'call_back': get_service_status,
      'time_max': 90,
      'value_type': 'uint',
      'units': 'N',
      'slope': 'both',
      'format': '%u',
      'description': 'Service Status module metric (shopply service)',
      'groups': 'service'}
  d2 = {'name': 'JenkinsService',
      'call_back': get_service_status,
      'time_max': 90,
      'value_type': 'uint',
      'units': 'N',
      'slope': 'both',
      'format': '%hu',
      'description': 'Service Status module metric (Jenkins service)',
      'groups': 'service'}
  descriptors = [d1,d2]
  return descriptors


def metric_cleanup():
  '''Clean up the service status module.'''
  pass


#This code is for debugging and unit testing    
if __name__ == '__main__':
  params = {'ShopplyPort': '8888', 'JenkinsPort': '8080'}
  metric_init(params)
  for d in descriptors:
    v = d['call_back'](d['name'])
    print 'value for %s is %u' % (d['name'],  v)

