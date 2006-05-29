# AboutDialog class
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

__version__ = '0.2.0529'

from wax import *
import wx

class AboutDialog(CustomDialog):
    """ Create About window. """
    
    def Body(self):
        import platform
        
        # Create dialog
        programName = Label(self, "lyricistCow %s" % __version__)
        programName.SetFont(('Verdana', 14))
        nb = NoteBook(self, size = (400,300))
        
        # About tab
        aboutTab = Panel(nb)
        
        aboutTab.copyrightText = _("lyricistCow - A simple lyrics viewer")
        aboutTab.copyrightText += "\n(c) 2006, Svoboda Vladimir"
        aboutTab.copyrightText += "\n<ze.vlad@gmail.com>\n"
        aboutTab.copyrightText += _("Lyrics provided by %s") % "leoslyrics"
        
        aboutTab.copyright = Label(aboutTab, aboutTab.copyrightText)
        aboutTab.AddComponent(aboutTab.copyright, border=10)
        aboutTab.Pack()
        nb.AddPage(aboutTab, _("About"))
        
        # License tab
        licenseTab = Panel(nb)
        license = open('COPYING', 'r')
        licenseTab.text = TextBox(licenseTab, multiline=1, Value=license.read())
        licenseTab.text.SetEditable(False)
        licenseTab.AddComponent(licenseTab.text, expand='both', border=5)
        licenseTab.Pack()
        nb.AddPage(licenseTab, _("License"))
        
        # Informations tab
        infoTab = Panel(nb)
        
        infoTab.infoText = _("System: %s") % platform.platform()
        infoTab.infoText += "\nPython: %s\nwxPython: %s" % (
                                   platform.python_version(), wx.VERSION_STRING)
        
        infoTab.AddComponent(Label(infoTab, infoTab.infoText), border=10)
        infoTab.Pack()
        nb.AddPage(infoTab, _("Informations"))
        
        # Window settings
        self.AddComponent(programName)
        self.AddSpace(10)
        self.AddComponent(nb, expand = 'both')
        self.AddComponent(Button(self, _("Close"), event=self.OnQuit),
                          border=3, align='center')
        self.Pack()
    
    def OnQuit(self, event=None):
        self.Close()