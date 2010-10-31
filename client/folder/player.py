#!/usr/bin/python
from AppKit import NSSound

import logging
import gflags
import os
import time
import urllib2
import urllib
import sys

gflags.DEFINE_bool('clear', False, 'Clear the catalog.')
gflags.DEFINE_bool('upload', False, 'Upload catalog.')
gflags.DEFINE_string('catalog', 'MyMusic', 'Catalog name.')
gflags.DEFINE_string('server', 'http://localhost:8080', 'Jukebox server.')
gflags.DEFINE_string('folder', '/Music', 'Folder containing mp3s.')
FLAGS = gflags.FLAGS


def CatalogExists():
  return eval(urllib2.urlopen('%s/rpc/catalog/exists?%s' % (
    FLAGS.server, urllib.urlencode({'catalog': FLAGS.catalog}))).read())


def UploadSongList():
  files = os.listdir(FLAGS.folder)
  songs = [('songs', x) for x in files]
  songs.append(('catalog', FLAGS.catalog))
  urllib2.urlopen('%s/rpc/catalog/upload' % FLAGS.server, urllib.urlencode(songs))


def ClearCatalog():
  urllib2.urlopen('%s/rpc/catalog/clear?%s' % (FLAGS.server, urllib.urlencode(
    {'catalog': FLAGS.catalog})))


def PlayNextSong():
  data = urllib2.urlopen('%s/rpc/nextsong' % FLAGS.server)
  filename = data.readline().strip()
  sound = NSSound.alloc()
  sound.initWithContentsOfFile_byReference_(os.path.join(FLAGS.folder, filename),
    True)
  sound.play()
  time.sleep(10)
  sound.stop()
  #while sound.isPlaying():
  #  time.sleep(1)


def main(argv):
  logging.basicConfig(level=logging.INFO)
  argv = FLAGS(argv)
  if FLAGS.clear:
    logging.info('Clearing catalog.')
    ClearCatalog()
  if not CatalogExists():
    logging.info('Uploading catalog.')
    UploadSongList()

  while True:
    PlayNextSong()
  

if __name__ == '__main__':
  main(sys.argv)
