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

  def get(self):
    user = users.User('nav@gmail.com')
    catalog_name = self.request.get('catalog')
    query = model.MusicCatalog.all()
    query.filter('name = ', catalog_name)
    catalog = query.fetch(1)[0]

    query = model.Vote.all()
    query.filter('user = ', user)
    query.filter('catalog = ', catalog)
    counts = {}
    for vote in query:
      counts[vote.song] = counts.get(vote.song, 0) + 1
    votes = []
    for (song, count) in counts.iteritems():
      votes.append({'song': song, 'count': count})
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
    filename = self.request.get('filename')
    user = users.User('nav@gmail.com')
    query = model.Song.all()
    query.filter('filename = ', filename)
    song = query.fetch(1)[0]
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
