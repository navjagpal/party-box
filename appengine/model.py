"""Datastore Model classes."""

from google.appengine.ext import db


class MusicCatalog(db.Model):
  name = db.StringProperty(required=True)
  owner = db.UserProperty(required=True)


class Song(db.Model):
  filename = db.StringProperty(required=True)
  catalog = db.ReferenceProperty(MusicCatalog)


class Vote(db.Model):
  user = db.UserProperty(required=True)
  song = db.ReferenceProperty(Song, required=True)
  catalog = db.ReferenceProperty(MusicCatalog)
