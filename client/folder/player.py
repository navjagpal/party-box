#!/usr/bin/python
"""Party-Box command line client for playing music from a folder of MP3s.

Note: This client is targetted at Mac OS. This should be made more general.

This is an example Party-Box client. It isn't intended for general use. It is provided
more for development purposes. It is likely to change frequently.

This client will use a folder of MP3s as the music catalog. It communicates with the
party-box back-end to manage the catalog and to determine playlist order.

./player --helpshort for more information.
"""

import gflags
import logging
import os
import sys
import time
import urllib2
import urllib

from AppKit import NSSound


gflags.DEFINE_bool('clear', False, 'Clear the catalog.')
gflags.DEFINE_bool('upload', False, 'Upload catalog.')
gflags.DEFINE_string('catalog', 'MyMusic', 'Catalog name.')
gflags.DEFINE_string('server', 'http://localhost:8080', 'Jukebox server.')
gflags.DEFINE_string('folder', '/Music', 'Folder containing mp3s.')
FLAGS = gflags.FLAGS


class FolderClient(object):
  """Party-Box client, handles communication with backend."""

  def __init__(self, server, catalog, folder):
    """Init.
  
    Args:
      server: URL for server, including http prefix.
      catalog: Name to use for the music catalog
      folder: Path to source music folder.
    """
    self._server = server
    self._catalog = catalog
    self._folder = folder
  
  def CatalogExists(self):
    """Returns True if catalog exists on server, False otherwise."""
    # TODO(nav): Eval'ing is definitely not the safest thing to do here.
    return eval(urllib2.urlopen('%s/rpc/catalog/exists?%s' % (
      self._server, urllib.urlencode(
        {'catalog': self._catalog}))).read())

  def ClearCatalog(self):
    """Clears catalog from server."""
    urllib2.urlopen('%s/rpc/catalog/clear?%s' % (
      self._server, urllib.urlencode(
      {'catalog': self._catalog})))

  def UploadSongList(self):
    """Uploads catalog information to server."""
    files = os.listdir(FLAGS.folder)
    songs = [('songs', x) for x in files]
    songs.append(('catalog', self._catalog))
    urllib2.urlopen('%s/rpc/catalog/upload' % self._server,
      urllib.urlencode(songs))

  def _PlayNextSong(self):
    data = urllib2.urlopen('%s/rpc/nextsong' % self._server)
    filename = data.readline().strip()
    sound = NSSound.alloc()
    sound.initWithContentsOfFile_byReference_(
      os.path.join(self._folder, filename), True)
    logging.info('Playing %s', filename)
    sound.play()
    time.sleep(10)
    sound.stop()

  def Run(self):
    while True:
      self._PlayNextSong()


def main(argv):
  # Setup logging.
  logging.basicConfig(level=logging.INFO)

  # Consume flags.
  argv = FLAGS(argv)

  client = FolderClient(FLAGS.server, FLAGS.catalog, FLAGS.folder)
  if FLAGS.clear:
    logging.info('Clearing catalog.')
    client.ClearCatalog()
  if not client.CatalogExists():
    logging.info('Uploading catalog.')
    client.UploadSongList()

  client.Run()
  

if __name__ == '__main__':
  main(sys.argv)
