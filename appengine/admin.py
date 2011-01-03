from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class Stats(webapp.RequestHandler):

  def get(self):
    stats = memcache.get_stats()
    self.response.out.write('<html><body>')
    self.response.out.write('<b>Cache Hits:%s</b><br/>' % stats['hits'])
    self.response.out.write('<b>Cache Misses:%s</b><br/>' %
                            stats['misses'])
    self.response.out.write('</body></html')


application = webapp.WSGIApplication(
  [('/admin/stats', Stats)], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
