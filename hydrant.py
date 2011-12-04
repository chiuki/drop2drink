import csv
import os
import urllib

from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class HydrantPage(webapp.RequestHandler):
  def get(self):
    number = int(self.request.path.split('/')[2])  # e.g. /hydrants/27
    data = self.fetch_data(number)

    path = os.path.join(os.path.dirname(__file__), 'templates/hydrant.html')
    if path is None:
      self.response.set_status(404)
      return

    self.response.out.write(template.render(path, data))

  def fetch_data(self, number):
    url = 'https://www.google.com/fusiontables/api/query'
    sql = 'SELECT * FROM 2331654 WHERE Number = %d' % number
    form_fields = {
      'sql': sql
    }
    form_data = urllib.urlencode(form_fields)
    result = urlfetch.fetch(url=url,
        payload=form_data,
        method=urlfetch.POST,
        headers={'Content-Type': 'application/x-www-form-urlencoded'})

    if result.status_code != 200:
      return None

    lines = result.content.strip().split('\n')

    if len(lines) != 2:
      return None

    reader = csv.reader(lines, skipinitialspace=True)
    keys = reader.next()
    values = reader.next()
    data = {}
    for i in xrange(len(keys)):
      key = keys[i]
      value = values[i]
      data[key] = value
    return data

handlers = [
  ('/hydrants/[0-9]+', HydrantPage)
]

application = webapp.WSGIApplication(handlers, debug=False)

def main():
  run_wsgi_app(application)
