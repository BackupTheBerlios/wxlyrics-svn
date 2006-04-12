#	Programmer:	Svoboda Vladimir
#	E-mail:	ze.vlad@gmail.com
#
#	Copyright 2006 Svoboda Vladimir
#
#	Distributed under the terms of the GPL (GNU Public License)
#
#	wxLyrics is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; either version 2 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Requirements (Dependencies):  Python, wxPython and waxgui.

# SearchLyrics class

import urllib
from xml.dom import minidom

class SearchLyrics:
    """ Search lyrics from artist and song title. """
        
    def SearchLyrics(self, artist, song):
        """ Get list of songs from leoslyrics.com """
        
        result = {}
        
        # Open a socket and analyse xml file to see results
        try:
            resultSock = urllib.urlopen('http://api.leoslyrics.com/api_search.php?auth=wxLyrics&artist=%s&songtitle=%s' %
                                        (urllib.quote(artist.encode('utf-8')), urllib.quote(song.encode('utf-8'))))
            resultDoc = minidom.parse(resultSock).documentElement
            resultSock.close()
            resultCode = resultDoc.getElementsByTagName('response')[0].getAttribute('code')
        
        except Exception, err:
            result["error"] = _("Cannot reach host")
            resultCode = 1
        
        if resultCode == '0':
            # Create list from result
            matches = resultDoc.getElementsByTagName('result')[:20]
            hid = map(lambda x: x.getAttribute('hid'), matches)
            songTitleDom = resultDoc.getElementsByTagName('title')[:20]
            songTitle = map(lambda x: x.firstChild.nodeValue, songTitleDom)
            artistNameDom = resultDoc.getElementsByTagName('name')[:20]
            artistName = map(lambda x: x.firstChild.nodeValue, artistNameDom)
            
            if len(hid) == 0:
                text = _("No lyrics found for this song")
            
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
            lyricsSock = urllib.urlopen("http://api.leoslyrics.com/api_lyrics.php?auth=QuodLibet&hid=%s" % ( urllib.quote(hid.encode('utf-8'))))
            lyricsDoc = minidom.parse(lyricsSock).documentElement
            lyricsSock.close()
            
            result["lyrics"] = lyricsDoc.getElementsByTagName('text')[0].firstChild.nodeValue
            lyricsDoc.unlink()
            
        except Exception, err:
            try: result["error"] = err.strerror.decode(locale.getpreferredencoding())
            except: result["error"] = _("Attempt to download lyrics failed")
        
        return result