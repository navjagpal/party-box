import logging
import model
import os
import random

from django.utils import simplejson

import gdata.youtube
import gdata.youtube.service

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


def GetCounterName(playlist_key, url):
  """Returns name for counter based on playlist and URL info.

  Args:
    playlist_key: playlist key (str) or Playlist object.
    url: YouTube video URL.
  Returns:
    Name suitable to use for calling model.increment()
  """
  if not isinstance(playlist_key, (str, unicode)):
    playlist_key = str(playlist_key.key())
  return '%s%s' % (playlist_key, url)


def GetUrlFromCounterName(playlist_key, counter_name):
  """Returns URL from the playlist_key.

  Args:
    playlist_key: playlist key (str) or Playlist object.
    counter_name: Full counter name.
  Returns:
    YouTube video URL.
  """ 
  if not isinstance(playlist_key, (str, unicode)):
    playlist_key = str(playlist_key.key())
  logging.info('Key = %s', playlist_key)
  return counter_name.split(playlist_key, 1)[1]


def GetYouTubeService():
  yt_service = gdata.youtube.service.YouTubeService()
  yt_service.developer_key = ('AI39si6ZT0-zdQXj2cYiOeF5ccTbYN5Ve4pJ0GbN6QhCV'
                              'KnTZvb-VpYfioFXeyGCjs-dHpCTQPjhwLY7xS2T_P_E1X'
                              'YHUMv2fQ')
  return yt_service


class Main(webapp.RequestHandler):

  def get(self):
    playlist_key = self.request.get('p', None)
    if playlist_key is None:
      logging.error('No playlist_key provided.')
      return self.error(404)  # TODO(nav): Better error.

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

    results = memcache.get('youtube-search:%s' % query)
    if results is None:
      yt_service = GetYouTubeService()
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
      results = simplejson.dumps(results)
      memcache.add('youtube-search:%s' % query, results)
    self.response.out.write(results)


class Add(webapp.RequestHandler):

  def get(self):
    url = self.request.get('url', None)
    title = self.request.get('title', None)
    playlist_key = self.request.get('p', None)
    if not url or not title or not playlist_key:
      return self.error(404)  # TODO(nav): Better error.

    # Is the user trying to cast a duplicate vote?
    playlist = model.Playlist.get(playlist_key)
    user = users.get_current_user()
    query = model.YouTubeVote.all().filter('playlist = ', playlist)
    query.filter('user = ', user)
    query.filter('url = ', url)
    if query.fetch(1):
      logging.info('User %s already voted for %s in playlist %s, not counting.',
                   user, url, playlist_key)
      self.response.out.write(simplejson.dumps(
        {'added': False, 'message': 'Already voted for this song.'}))
    else:
      model.YouTubeVideo.get_or_insert(url, url=url, title=title)
      model.increment(playlist_key, GetCounterName(playlist_key, url)) 
      vote = model.YouTubeVote(user=user, playlist=playlist, url=url)
      vote.put()
      self.response.out.write(simplejson.dumps({'added': True}))


def GetSortedPlaylist(playlist):
  if isinstance(playlist, (str, unicode)):
    playlist = model.Playlist.get(playlist)
  configs = model.GeneralCounterShardConfig.all().filter(
    'playlist =', playlist)
  results = []
  for config in configs:
    url = GetUrlFromCounterName(playlist, config.name)
    title = memcache.get('youtube-title:%s' % url)
    if title is None:
      video = model.YouTubeVideo.get_by_key_name(url)
      title = video.title
      memcache.add('youtube-title:%s' % url, title)
    results.append({'url': url, 'title': title,
                    'count': model.get_count(config.name)})
  results.sort(lambda x, y: cmp(y['count'], x['count']))
  return results


class Playlist(webapp.RequestHandler):

  def get(self):
    playlist_key = self.request.get('p', None)
    if playlist_key is None:
      return self.error(404)  # TODO(nav): Better error.

    results = GetSortedPlaylist(playlist_key)
    self.response.out.write(simplejson.dumps(results))


class NextSong(webapp.RequestHandler):

  def get(self):
    user = users.get_current_user()
    playlist = model.Playlist.get_by_key_name(user.user_id())
    if not playlist:
      # This shouldn't happen since the user has already hit the player.
      return self.error(404)  # TODO(nav): Better error.

    songs = GetSortedPlaylist(playlist)
    if not songs:
      self.redirect('/youtube/player/randomsong')
    else:
      model.delete_counter(GetCounterName(playlist, songs[0]['url']))
      # Delete all votes for this song too, so people can add this song back if they
      # want to.
      # TODO(nav): This could be an issue if there are many vote entries for a song
      # because it could take too long to delete them all.
      query = model.YouTubeVote.all().filter('playlist = ', playlist).filter(
        'url = ', songs[0]['url'])
      for result in query:
        result.delete()
      result = {'url': songs[0]['url']}
      self.response.out.write(simplejson.dumps(result))


class RandomPopularSong(webapp.RequestHandler):
  """Provides a random popular YouTube video.

  This is so we can offer a song even if the playlist is empty. There should
  be different sources, Last.fm for example.
  """

  def get(self):
    feed = memcache.get('popular-youtube-feed')
    if feed is None:
      yt_service = GetYouTubeService()
      feed = yt_service.GetYouTubeVideoFeed(
        'http://gdata.youtube.com/feeds/api/videos/-/Music/?orderby=viewCount')
      memcache.add('popular-youtube-feed', feed)
  
    entry = random.choice(feed.entry)  
    result = {'url': entry.GetSwfUrl(),
              'title': entry.media.title.text}
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
