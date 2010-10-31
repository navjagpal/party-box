"""Handles Jukebox mode."""

import logging
import model
import os
import random

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


class PartyList(webapp.RequestHandler):
  """Displays a list of parties/catalogs."""

  def get(self):
    query = model.MusicCatalog.all()
    catalogs = [x for x in query]
    template_values = {
      'catalogs': catalogs
    }
    path = os.path.join(os.path.dirname(__file__),
      'templates/partylist.html')
    self.response.out.write(template.render(path, template_values))


class PartyView(webapp.RequestHandler):
  """Displays the current playlist/votes and list of available songs."""

  def get(self):
    user = users.get_current_user()
    catalog_id = int(self.request.get('catalog'))
    query = model.MusicCatalog.get_by_id([catalog_id])
    catalog = query[0]

    query = model.Vote.all()
    query.filter('catalog = ', catalog)
    counts = {}
    key_to_song = {}
    for vote in query:
      counts[vote.song.key().id()] = counts.get(vote.song.key().id(), 0) + 1
      key_to_song[vote.song.key().id()] = vote.song
    votes = []
    for (id, count) in counts.iteritems():
      votes.append({'song': key_to_song[id], 'count': count})
    logging.info('Votes = %s', votes)

    query = model.Song.all()
    query.filter('catalog = ', catalog)
    songs = [song for song in query]
    template_values = {
      'votes': votes,
      'songs': songs
    }

    path = os.path.join(os.path.dirname(__file__),
      'templates/partyview.html')
    self.response.out.write(template.render(path, template_values))


class PartyVote(webapp.RequestHandler):

  def get(self):
    user = users.get_current_user()
    song_id = int(self.request.get('song'))
    query = model.Song.get_by_id([song_id])
    song = query[0]
   
    query = model.Vote.all()
    query.filter('user = ', user)
    query.filter('song = ', song)
    if query.fetch(1):
      logging.info('Already voted.')
      return
    vote = model.Vote(user=user, song=song, catalog=song.catalog)
    vote.put() 
          

application = webapp.WSGIApplication(
  [('/jukebox/list', PartyList),
   ('/jukebox/view', PartyView),
   ('/jukebox/vote', PartyVote)], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main() 
