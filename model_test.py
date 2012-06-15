import json
import httplib
from hello_es import Model


def _test_message(msg_dict):
  print(msg_dict)
  assert msg_dict[u"status"] == 200
  assert msg_dict[u"ok"] == True


def testElasticSearch():
  msg_dict = Model().get_message()
  _test_message(msg_dict['allinfo'])


def testTornado():
  conn = httplib.HTTPConnection('localhost:8888')
  headers = {"Accept": "application/json"}
  conn.request('GET', '', '', headers)
  response = conn.getresponse()
  message = response.read()
  conn.close()
  assert response.status == 200
  msg_dict = json.loads(message)
  _test_message(msg_dict)


