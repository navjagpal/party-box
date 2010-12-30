import logging
import model
import os
import random

from django.utils import simplejson

import gdata.youtube
import gdata.youtube.service

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Main(webapp.RequestHandler):

  def get(self):
    playlist_key = self.request.get('p', None)
    if playlist_key is None:
      logging.error('No playlist_key provided.')
      return self.error(404)  # TODO(nav): Better error.

    logging.info('Got key %s', playlist_key)
    playlist = model.Playlist.get(playlist_key)
    if not playlist:
      logging.error('Invalid playlist_key')
      return self.error(404)  # TODO(nav): Better error.

    path = os.path.join(os.path.dirname(__file__),
      'templates/youtube.html')
    self.response.out.write(
      template.render(path, {'playlist': playlist_key}))


class Player(webapp.RequestHandler):

  def get(self):
    user = users.get_current_user()
    playlist = model.Playlist.get_or_insert(user.user_id(), owner=user)
    path = os.path.join(os.path.dirname(__file__),
      'templates/youtube_player.html')
    self.response.out.write(
      template.render(path, {'playlist': str(playlist.key())}))
  

class Search(webapp.RequestHandler):

  def get(self):
    query = self.request.get('q', None)
    if query is None:
      return self.error(404)  # TODO(nav): Better error.
    
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
    playlist_key = self.request.get('p', None)
    if not url or not playlist_key:
      return self.error(404)  # TODO(nav): Better error.
   
    model.increment(url) 
    self.response.out.write('OK')


def GetSortedPlaylist():
  configs = model.GeneralCounterShardConfig.all()
  results = []
  for config in configs:
    results.append((config.name, model.get_count(config.name)))
  results.sort(lambda x, y: cmp(y[1], x[1]))
  return results


class Playlist(webapp.RequestHandler):

  def get(self):
    playlist_key = self.request.get('p', None)
    if playlist_key is None:
      return self.error(404)  # TODO(nav): Better error.

    results = GetSortedPlaylist()
    self.response.out.write(simplejson.dumps(results))


class NextSong(webapp.RequestHandler):

  def get(self):
    user = users.get_current_user()
    playlist = model.Playlist.get_by_key_name(user.user_id())
    if not playlist:
      # This shouldn't happen since the user has already hit the player.
      return self.error(404)  # TODO(nav): Better error.

    songs = GetSortedPlaylist()
    if not songs:
      self.redirect('/youtube/player/randomsong')
    else:
      model.delete_counter(songs[0][0])
      result = {'url': songs[0][0]}
      self.response.out.write(simplejson.dumps(result))


class RandomPopularSong(webapp.RequestHandler):
  """Provides a random popular YouTube video.

  This is so we can offer a song even if the playlist is empty. There should
  be different sources, Last.fm for example.
  """

  def get(self):
    yt_service = gdata.youtube.service.YouTubeService()
    feed = yt_service.GetYouTubeVideoFeed(
      'http://gdata.youtube.com/feeds/api/videos/-/Music/?orderby=viewCount')
  
    entry = random.choice(feed.entry)  
    result = {'url': entry.GetSwfUrl()}
    self.response.out.write(simplejson.dumps(result))


application = webapp.WSGIApplication(
  [('/youtube', Main),
   ('/youtube/search', Search),
   ('/youtube/add', Add),
   ('/youtube/playlist', Playlist),
   ('/youtube/player', Player),
   ('/youtube/player/next', NextSong),
   ('/youtube/player/randomsong', RandomPopularSong)], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
