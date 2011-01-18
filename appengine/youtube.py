import logging
import model
import os
import random
import re

from django.utils import simplejson

import gdata.youtube
import gdata.youtube.service

from google.appengine.api import channel
from google.appengine.api import mail
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


SHORTENER_URL = ('https://www.googleapis.com/urlshortener/v1/url'
		 '?key=AIzaSyA8OdrL9Xh0ebjKWOMVrnzRP_pw9TaTuws')


def GetCounterName(playlist_key, id):
  """Returns name for counter based on playlist and ID info.

  Args:
    playlist_key: playlist key (str) or Playlist object.
    id: YouTube video ID.
  Returns:
    Name suitable to use for calling model.increment()
  """
  if not isinstance(playlist_key, (str, unicode)):
    playlist_key = str(playlist_key.key())
  return '%s%s' % (playlist_key, id)


def GetIdFromCounterName(playlist_key, counter_name):
  """Returns ID from the playlist_key.

  Args:
    playlist_key: playlist key (str) or Playlist object.
    counter_name: Full counter name.
  Returns:
    YouTube video ID.
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


def GetIdFromUrl(url):
  m = re.match('http://[^\/]+\/v\/([^?]+)', url)
  if m:
    return m.group(1)
  return None
 

def GetShortUrl(self, base_url, playlist_id):
  """Makes request to Google URL Shortener and returns result.
  
  Args:
    base_url: Base URL for playlist.
    playlist_id: Playlist id, str.
  Returns:
    Short URL, str or None if error.
  """
  url = '%s/playlist?p=%s' % (base_url, playlist_id)
  result = urlfetch.fetch(
    url=SHORTENER_URL,
    headers={'Content-Type': 'application/json'},
    method=urlfetch.POST,
    payload=simplejson.dumps({'longUrl': url}))
  if result.status_code == 200:
    logging.info('Result = %s', result.content)
    response = simplejson.loads(result.content)
    return response['id']
  else:
    return None


class BaseHandler(webapp.RequestHandler):

  def __init__(self, desktop_template, mobile_template=None):
    super(BaseHandler, self).__init__()
    self._desktop_template = desktop_template
    self._mobile_template = mobile_template
 
  def _IsMobileRequest(self):
    # TODO(nav): Implement this for real.
    return 'Android' in self.request.user_agent

  def _WriteResponse(self, template_values):
    if self._mobile_template and self._IsMobileRequest():
      template_file = self._mobile_template
    else:
      template_file = self._desktop_template
    path = os.path.join(os.path.dirname(__file__), template_file)
    self.response.out.write(
      template.render(path, template_values))


class PlaylistEditor(BaseHandler):

  def __init__(self):
    super(PlaylistEditor, self).__init__(
      'templates/youtube_playlist.html',
      'templates/youtube_playlist_mobile.html')

  def get(self):
    playlist_key = self.request.get('p', None)
    if playlist_key is None:
      logging.error('No playlist_key provided.')
      return self.error(404)  # TODO(nav): Better error.

    playlist = model.Playlist.get(playlist_key)
    if not playlist:
      logging.error('Invalid playlist_key')
      return self.error(404)  # TODO(nav): Better error.

    self._WriteResponse({'playlist': playlist_key})


class Player(webapp.RequestHandler):

  def get(self):
    user = users.get_current_user()
    playlist = model.Playlist.get_or_insert(user.user_id(), owner=user)
    path = os.path.join(os.path.dirname(__file__),
      'templates/youtube_player.html')
    token = channel.create_channel(user.user_id())
    self.response.out.write(
      template.render(path, {'playlist': str(playlist.key()),
			     'link': playlist.link,
			     'token': token}))


class SharePlaylist(webapp.RequestHandler):

  def get(self):
    email = self.request.get('email', None);
    results = {'success': False}
    if email is None or not mail.is_email_valid(email):
      logging.warn('Invalid email:%s', email)
      results['error'] = 'Invalid address.'
    else:
      user = users.get_current_user()
      playlist = model.Playlist.get_or_insert(user.user_id(), owner=user)
      if playlist.link:
	short_link = playlist.link
      else:
	short_link = GetShortUrl('http://party-box.appspot.com',
	  str(playlist.key()))
      sender_address = 'PartyBox <noreply@party-box.appspotmail.com>'
      subject = 'Playlist Invitation'
      body = """
Hello %s,\n\n
%s would like you to check out their playlist on PartyBox. You can add
songs to the playlist, or vote on existing songs.\n\n
%s
""" % (email, user.email(), short_link)
      mail.send_mail(sender_address, email, subject, body)
      results['success'] = True
    self.response.out.write(simplejson.dumps(results))
 

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
	if not entry.GetSwfUrl():
	  continue
        id = GetIdFromUrl(entry.GetSwfUrl())
	if not id:
	  logging.warn('Problem getting ID from URL %s',
		       entry.GetSwfUrl())
	  continue
        thumbnails = [x.url for x in entry.media.thumbnail]
        results.append({'title': title, 'id': id,
                        'thumbnails': thumbnails})
      results = simplejson.dumps(results)
      memcache.add('youtube-search:%s' % query, results)
    self.response.out.write(results)


class Add(webapp.RequestHandler):

  def get(self):
    id = self.request.get('id', None)
    title = self.request.get('title', None)
    thumbnails = self.request.get('thumbnail', allow_multiple=True)
    playlist_key = self.request.get('p', None)
    if not id or not title:
      return self.error(404)  # TODO(nav): Better error.

    # If not supplied, return the users own playlist.
    if playlist_key is None:
      user = users.get_current_user()
      playlist = model.Playlist.get_or_insert(user.user_id(), owner=user)
      playlist_key = str(playlist.key())
    
    # Is the user trying to cast a duplicate vote?
    playlist = model.Playlist.get(playlist_key)
    user = users.get_current_user()
    query = model.YouTubeVote.all().filter('playlist = ', playlist)
    query.filter('user = ', user)
    query.filter('id = ', id)
    if query.fetch(1):
      logging.info('User %s already voted for %s in playlist %s, not counting.',
                   user, id, playlist_key)
      self.response.out.write(simplejson.dumps(
        {'added': False, 'message': 'Already voted for this song.'}))
    else:
      model.YouTubeVideo.get_or_insert(
        id, title=title,
        thumbnails=thumbnails)
      model.increment(playlist_key, GetCounterName(playlist_key, id)) 
      vote = model.YouTubeVote(user=user, playlist=playlist, id=id)
      vote.put()

      # Return the current count for this entry, along with metadata.
      entry = { 'id': id, 'title': title, 'thumbnails': thumbnails,
		'count': model.get_count(GetCounterName(
		  playlist, id)), 'voted': True }

      self.response.out.write(simplejson.dumps(
	{'added': True, 'entry': entry}))


def GetSortedPlaylist(playlist):
  if isinstance(playlist, (str, unicode)):
    playlist = model.Playlist.get(playlist)

  # Build a dict of votes this user has casted.
  voted = {}
  user = users.get_current_user()
  query = model.YouTubeVote.all().filter('playlist = ', playlist)
  query.filter('user = ', user)
  for vote in query:
    voted[vote.id] = True

  configs = model.GeneralCounterShardConfig.all().filter(
    'playlist =', playlist)
  results = []
  for config in configs:
    # TODO(nav): Consider caching title/thumbnail info.
    id = GetIdFromCounterName(playlist, config.name)
    video = model.YouTubeVideo.get_by_key_name(id)
    results.append({'id': id, 'title': video.title,
                    'thumbnails': video.thumbnails,
                    'count': model.get_count(config.name),
		    'voted': id in voted})
  results.sort(lambda x, y: cmp(y['count'], x['count']))
  return results


class Playlist(webapp.RequestHandler):

  def get(self):
    playlist_key = self.request.get('p', None)
    # If not supplied, return the users own playlist.
    if playlist_key is None:
      user = users.get_current_user()
      playlist = model.Playlist.get_or_insert(user.user_id(), owner=user)
      playlist_key = str(playlist.key())

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
      model.delete_counter(GetCounterName(playlist, songs[0]['id']))
      # Delete all votes for this song too, so people can add this song back if they
      # want to.
      # TODO(nav): This could be an issue if there are many vote entries for a song
      # because it could take too long to delete them all.
      query = model.YouTubeVote.all().filter('playlist = ', playlist).filter(
        'id = ', songs[0]['id'])
      for result in query:
        result.delete()

      video = model.YouTubeVideo.get_by_key_name(songs[0]['id'])
      result = {'id': video.key().name(), 'title': video.title,
                'thumbnails': video.thumbnails,
		'nowPlaying': True,
		'count': songs[0]['count']}
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
    result = {'id': GetIdFromUrl(entry.GetSwfUrl()),
              'title': entry.media.title.text,
	      'random': True,
              'thumbnails': [x.url for x in entry.media.thumbnail]}
    self.response.out.write(simplejson.dumps(result))


class RemoteControl(webapp.RequestHandler):
  """Provides remote control operations for the player."""

  def get(self):
    # This simply forwards the "op" parameter to the player.
    user = users.get_current_user()
    op = self.request.get('op', None)
    success = False
    if op is not None:
      success = True
      channel.send_message(
	user.user_id(), simplejson.dumps({'op': op}))
    self.response.out.write(
      simplejson.dumps({'success': success}))


application = webapp.WSGIApplication(
  [('/playlist', PlaylistEditor),
   ('/youtube/search', Search),
   ('/youtube/add', Add),
   ('/youtube/playlist/share', SharePlaylist),
   ('/youtube/playlist', Playlist),
   ('/youtube/remote', RemoteControl),
   ('/player', Player),
   ('/youtube/player/next', NextSong),
   ('/youtube/player/randomsong', RandomPopularSong)], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
