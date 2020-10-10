#!/usr/bin/python

import sys
import re
import os
import shutil
import commands
import json
import s3Uploader

def get_music_metadata(dir):
  """
  Directory structure must be /root/artist/albumName/songs.mp3
  """
  artistDirResults = []
  artists = []
  albums = []
  songs = []
  uploaderInputs = []
  counter = 1

  artistDirs = os.listdir(dir)
  for artistDir in artistDirs:
    artists.append(artistDir)
    fullArtistDir = os.path.abspath(os.path.join(dir, artistDir))
    albumDirs = os.listdir(fullArtistDir)
    for albumDir in albumDirs:
      if not albumDir.startswith('.'):
        fullAlbumDir = os.path.abspath(os.path.join(fullArtistDir, albumDir))
        albums.append(albumDir)
        songFileNames = os.listdir(fullAlbumDir)
        for songFileName in songFileNames:
          if not songFileName.startswith('.'):
            cleanedFileName = cleanFileName(songFileName)
            
            fullSongFileNamePath = os.path.abspath(os.path.join(fullAlbumDir, songFileName))
            key = artistDir + '/' + albumDir + '/' + songFileName
            uploaderInput = (fullSongFileNamePath, key)
            # print uploaderInput
            uploaderInputs.append(uploaderInput)

            song = {
              "id": counter,
              "artist": artistDir,
              "songTitle": cleanedFileName,
              "url": songFileName
            }
            songJsonObj = song ##json.dumps(song)
            artistDirResults.append(songJsonObj)
            counter += 1

  dictStruct = {
    "songList": artistDirResults,
    "artistList": artists,
    "albumList": albums
  }

  jsonStr = json.dumps(dictStruct, indent=4)

  file = open("temp.json", 'w')
  fullJsonPath = os.path.abspath(file.name)
  file.write(jsonStr)
  file.close()
  
  return (fullJsonPath, uploaderInputs)

def cleanFileName(filename):
  cleanedFileName = filename[:-4]
  cleanedFileName = re.sub(r'\d+', '', cleanedFileName)
  return cleanedFileName.strip()

MUSIC_GENERATOR_FILE = '<path>/my-jukebox-musicGenerator/musicGenerator' 
def write_to_mysql(result, songListName, graphicURL):
  cmd = r'node  %s %s %s %s' % (MUSIC_GENERATOR_FILE, result, songListName, graphicURL)
  print cmd
  try:
    (status, output) = commands.getstatusoutput(cmd)
    print status
    print output
    if status:
      sys.stderr.write(output)
      sys.exit(status)
      print output
  except:
    print 'error: ' + status
    print 'output: ' + output 

def main():
  """
    albumFileName will be the graphic used in cover flow to represent the list.
    copy your graphic to the images folder in the web application.
    i.e. my-jukebox/public/images

    --graphicFileName rock3.jpg

  """
  args = sys.argv[1:]
  if not args:
    print "usage: [--songlistName name][--graphicFileName filename] dir [dir ...]";
    sys.exit(1)

  songListName = ''
  if args[0] == '--songListName':
    songListName = args[1]
    del args[0:2]
  else:
    print 'error: please specify --songlistName'

  graphicURL = ''
  if args[0] == '--graphicURL':
    graphicURL = args[1]
    del args[0:2]
  else:
    print 'error: please specify --graphicURL'

  if len(args) == 0:
    print "error: must specify a root dir of music"
    sys.exit(1)

  dir = args[0]
  result = get_music_metadata(dir)
  uploaderInputs = result[1]
  for uploaderInput in uploaderInputs:
    localFile = uploaderInput[0]
    key = uploaderInput[1]
    s3Uploader.upload(localFile, key)

  write_to_mysql(result[0], songListName, graphicURL)
  
  
if __name__ == "__main__":
  main()
