# SearchLyrics class
#
# Copyright 2006 Vladimir Svoboda
#
# This file is a part of The Musical Cow suite
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
# $Id$

import sys
import urllib
from xml.dom import minidom

class SearchLyrics:
    """ Search lyrics from artist and song title. """
        
    def SearchLyrics(self, artist, song):
        """ Get list of songs from leoslyrics.com """
        
        result = {}
        
        # Open a socket and analyse XML file to see results
        try:
            
            resultSock = urllib.urlopen(
             'http://api.leoslyrics.com/api_search.php?auth=TheMusicalCow'
             '&artist=%s&songtitle=%s' % (urllib.quote(artist.encode('utf-8')),
                                          urllib.quote(song.encode('utf-8'))))
            resultDoc = minidom.parse(resultSock).documentElement
            resultSock.close()
            resultCode = resultDoc.getElementsByTagName('response')[0].getAttribute('code')
        
        except Exception, err:
            sys.stderr.write("Cannot reach host: %s" % err)
            #result["error"] = _("Cannot reach host")
            resultCode = 1
        
        if resultCode == '0':
            # Create list from result
            matches = resultDoc.getElementsByTagName('result')[:50]
            hid = map(lambda x: x.getAttribute('hid'), matches)
            songTitleDom = resultDoc.getElementsByTagName('title')[:50]
            songTitle = map(lambda x: x.firstChild.nodeValue, songTitleDom)
            artistNameDom = resultDoc.getElementsByTagName('name')[:50]
            artistName = map(lambda x: x.firstChild.nodeValue, artistNameDom)
            
            songList = {}
            i = 0
            
            # Create a list[artist name, song title, hid]
            for results in zip(artistName, songTitle):
                list = [results[0], results[1], hid[i]]
                songList[i] = list
                i += 1
                
            result["songlist"] = songList
            resultDoc.unlink()
            
        return result
    
    def ShowLyrics(self, hid):
        """ Download lyrics. """
        
        result = {}
        
        try:
            lyricsSock = urllib.urlopen(
             'http://api.leoslyrics.com/api_lyrics.php?auth=TheMusicalCow'
             '&hid=%s' % ( urllib.quote(hid.encode('utf-8'))))
            lyricsDoc = minidom.parse(lyricsSock).documentElement
            lyricsSock.close()
            
            try: result["album"] = lyricsDoc.getElementsByTagName('name')[1].firstChild.nodeValue
            except Exception, err: result["album"] = _("Unknow Album")
            
            result["lyrics"] = lyricsDoc.getElementsByTagName('text')[0].firstChild.nodeValue
            lyricsDoc.unlink()
            
        except Exception, err:
            try: result["error"] = err.strerror.decode(locale.getpreferredencoding())
            except:
                sys.stderr.write("Attempt to download lyrics failed")
                result["error"] = _("Attempt to download lyrics failed")
        
        return result