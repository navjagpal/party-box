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

  def get(self):
    songs = []
    for song in model.Song.all():
      songs.append(song)
    song = random.choice(songs)
    self.response.out.write(song.filename)


application = webapp.WSGIApplication(
  [('/rpc/catalog/upload', UploadSonglist),
   ('/rpc/catalog/clear', ClearCatalog),
   ('/rpc/catalog/exists', CatalogExists),
   ('/rpc/nextsong', NextSong)], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main() 
