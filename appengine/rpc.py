"""Handles /rpc requests from clients."""

import logging
import model
import random

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class UploadSonglist(webapp.RequestHandler):

  def post(self):
    user = users.User('nav@gmail.com')
    name = self.request.get('catalog')
    songs = self.request.get('songs', allow_multiple=True)
    logging.info('Songs = %s', songs)
    catalog = model.MusicCatalog(name=name, owner=user)
    catalog.put()
    for song in songs:
      s = model.Song(filename=song.strip(), catalog=catalog)
      s.put()


class ClearCatalog(webapp.RequestHandler):

  def get(self):
    name = self.request.get('catalog')
    owner = users.User('nav@gmail.com')
    query = model.MusicCatalog.all()
    query.filter('owner = ', owner)
    query.filter('name = ', name)
    for catalog in query:
      song_q = Song.all()
      song_q.filter('catalog = ', catalog)
      for song in song_q:
        song.delete()
      catalog.delete()


class CatalogExists(webapp.RequestHandler):

  def get(self):
    name = self.request.get('catalog')
    owner = users.User('nav@gmail.com')
    query = model.MusicCatalog.all()
    query.filter('owner = ', owner)
    query.filter('name = ', name)
    c = []
    for x in query:
      c.append(x)
    if c:
      self.response.out.write('True')
    else:
      self.response.out.write('False')    


class NextSong(webapp.RequestHandler):
  """Returns the next song to play and removes it from the list.

  This isn't fully implemented. Right now it just returns a random song that has at least
  one vote.
  """

  def get(self):
    owner = users.User('nav@gmail.com')
    catalog = self.request.get('catalog')
    logging.info('Catalog for next song: %s' % catalog)
    
    query = model.MusicCatalog.all()
    query.filter('owner = ', owner)
    query.filter('name = ', catalog)
    catalog = query.fetch(1)[0]

    query = model.Vote.all()
    query.filter('catalog = ', catalog)
    c = []
    for x in query:
      c.append(x)

    vote = random.choice(c)
    name = vote.song.filename
    vote.delete()
    self.response.out.write(name)
    

application = webapp.WSGIApplication(
  [('/rpc/catalog/upload', UploadSonglist),
   ('/rpc/catalog/clear', ClearCatalog),
   ('/rpc/catalog/exists', CatalogExists),
   ('/rpc/nextsong', NextSong)], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main() 
