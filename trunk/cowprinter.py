# PreferencesDialog class
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

import wx.html

class Printer(wx.html.HtmlEasyPrinting):
    """ Print HTML code. """
    
    def __init__(self, artist, song, lyrics, toprint=1):
        wx.html.HtmlEasyPrinting.__init__(self)
        self.GenerateHTML("%s - %s" % (artist, song), lyrics)
        
        if toprint:
            self.PrintText(text)
    
    def GenerateHTML(header, content):
        """ Generate HTML code. """
        
        HTML = "<h3 align=\"center\">%s</h3><br><br>" \
               "<span style=\"font-size: 10pt\">%s</span>" % (header, content)
        
        return HTML.encode('latin-1', 'replace').replace('\n', '<br>')
