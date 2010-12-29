import logging
import model
import os

from django.utils import simplejson

import gdata.youtube
import gdata.youtube.service

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Main(webapp.RequestHandler):

  def get(self):
    path = os.path.join(os.path.dirname(__file__),
      'templates/youtube.html')
    self.response.out.write(template.render(path, {}))


class Search(webapp.RequestHandler):

  def get(self):
    query = self.request.get('q', None)
    if query is None:
      self.error(404)  # TODO(nav): Better error.
    
    yt_service = gdata.youtube.service.YouTubeService()
    yt_query = gdata.youtube.service.YouTubeVideoQuery()
    yt_query.vq = query
    yt_query.orderby = 'relevance'
    yt_query.racy = 'include'
    yt_query.categories.append('/Music')
    feed = yt_service.YouTubeQuery(yt_query)
    
    results = []
    for entry in feed.entry:
      title = entry.media.title.text
      url = entry.GetSwfUrl()
      thumbnails = [x.url for x in entry.media.thumbnail]
      results.append({'title': title, 'url': url,
                      'thumbnails': thumbnails})
    self.response.out.write(simplejson.dumps(results))


class Add(webapp.RequestHandler):

  def get(self):
    url = self.request.get('url', None)
    if url is None:
      self.error(404)  # TODO(nav): Better error.
   
    model.increment(url) 
    self.response.out.write('OK')


class Playlist(webapp.RequestHandler):

  def get(self):
    configs = model.GeneralCounterShardConfig.all()
    results = []
    for config in configs:
      results.append((config.name, model.get_count(config.name)))
    results.sort(lambda x, y: cmp(y[1], x[1]))
    self.response.out.write(simplejson.dumps(results))


application = webapp.WSGIApplication(
  [('/youtube', Main),
   ('/youtube/search', Search),
   ('/youtube/add', Add),
   ('/youtube/playlist', Playlist)], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
