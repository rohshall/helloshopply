import socket


descriptors = []


port_map = {'ShopplyService': 8888, 'JenkinsService': 8080, 'ElasticsearchService': 9200}


def get_service_status(service_name):
  '''Return the service status.'''
  port = port_map[service_name]
  # check whether we can access this service from the host
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.settimeout(6)
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
  descriptors = [
    {'name': service,
      'call_back': get_service_status,
      'time_max': 90,
      'value_type': 'uint',
      'units': 'N',
      'slope': 'both',
      'format': '%u',
      'description': 'Service Status module metric (%s)' % service,
      'groups': 'service'}
    for service in port_map]
  return descriptors


def metric_cleanup():
  '''Clean up the service status module.'''
  pass


# This code is for debugging and unit testing    
if __name__ == '__main__':
  params = dict((service.replace('Service', 'Port'), port) for service, port in port_map.iteritems())
  metric_init(params)
  print descriptors
  for d in descriptors:
    v = d['call_back'](d['name'])
    print 'value for %s is %u' % (d['name'],  v)

