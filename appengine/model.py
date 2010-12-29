"""Datastore Model classes."""

import random

from google.appengine.api import memcache
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


class GeneralCounterShardConfig(db.Model):
  name = db.StringProperty(required=True)
  num_shards = db.IntegerProperty(required=True, default=5)


class GeneralCounterShard(db.Model):
  name = db.StringProperty(required=True)
  count = db.IntegerProperty(required=True, default=0)


def get_count(name):
  total = memcache.get(name)
  if total is None:
    total = 0
    for counter in GeneralCounterShard.all().filter('name = ', name):
      total += counter.count
    memcache.add(name, str(total), 60)
  return int(total)


def increment(name):
  config = GeneralCounterShardConfig.get_or_insert(name, name=name)
  def txn():
    index = random.randint(0, config.num_shards - 1)
    shard_name = name + str(index)
    counter = GeneralCounterShard.get_by_key_name(shard_name)
    if counter is None:
      counter = GeneralCounterShard(key_name=shard_name, name=name)
    counter.count += 1
    counter.put()
  db.run_in_transaction(txn)
  memcache.incr(name)


def delete_counter(name):
  config = GeneralCounterShardConfig.get_by_key_name(name)
  if not config:
    return
  # TODO(nav): Does this need to run in a txn?
  for counter in GeneralCounterShard.all().filter('name = ', name):
    counter.delete()
  config.delete()
  memcache.delete(name)
