#
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

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

import sys, os
sys.path.append(os.path.join(os.getcwd(), "../"))

import locale, gettext, ConfigParser
import wax, wx.html
from wax.tools.choicedialog import ChoiceDialog
from searchlyrics import SearchLyrics

class Printer(wx.html.HtmlEasyPrinting):
    """ Prints HTML code. """
    
    def __init__(self, parent):
        wx.html.HtmlEasyPrinting.__init__(self)
        self.parent = parent
        
    def Print(self, text, linenumbers = 1):
        self.PrintText(text)

class MainFrame(wax.Frame):
    """ Main window with menu, status bar and notebook (tabs) for lyrics. """
    def Body(self):
        self.result = [None]
        self.filename = [None]
        
        # Create status bar
        self.statusBar = wax.StatusBar(self, numpanels=2)
        self.SetStatusBar(self.statusBar)
        
        # Create menu and body
        self.CreateMenu()
        self.CreateBody()
        
    def CreateBody(self):
        """ Contenu de la frame """
        
        # Vertical panel: buttons ; notebook
        self.vPanel = wax.VerticalPanel(self)
        
        # Buttons
        self.vPanel.hPanelInput = wax.HorizontalPanel(self.vPanel)
        
        self.vPanel.hPanelInput.artistInput = wax.TextBox(self.vPanel.hPanelInput, _("Artist"))
        self.vPanel.hPanelInput.songInput = wax.TextBox(self.vPanel.hPanelInput, _("Song title"))
        self.vPanel.hPanelInput.searchButton = wax.Button(self.vPanel.hPanelInput, _("Search"), event=self.OnSearch)
        
        self.vPanel.hPanelInput.AddComponent(self.vPanel.hPanelInput.artistInput, border = 5)
        self.vPanel.hPanelInput.AddComponent(self.vPanel.hPanelInput.songInput, border = 5)
        self.vPanel.hPanelInput.AddComponent(self.vPanel.hPanelInput.searchButton, border = 5)
        self.vPanel.hPanelInput.Pack()
        
        # NoteBook
        self.vPanel.noteBook = wax.NoteBook(self.vPanel, size = (400, 300))
        self.vPanel.noteBook.tab = [wax.Panel(self.vPanel.noteBook)]
        
        # Tabs
        self.usedTab = [False]
        self.currentTab = 0
        self.vPanel.noteBook.tab[0].lyricsText = wax.TextBox(self.vPanel.noteBook.tab[0], multiline=1, Value = _("Lyrics"))
        self.vPanel.noteBook.tab[0].AddComponent(self.vPanel.noteBook.tab[0].lyricsText, expand = 'both')
        self.vPanel.noteBook.AddPage(self.vPanel.noteBook.tab[0], _("Untitled %s") % 1)
        self.vPanel.noteBook.tab[0].Pack()
        
        self.vPanel.AddComponent(self.vPanel.hPanelInput, border = 5)
        self.vPanel.AddComponent(self.vPanel.noteBook, expand = 'both')
        self.vPanel.Pack()
        
        self.AddComponent(self.vPanel, expand = 'both')
        
        # Window Settings
        self.SetSize((450, 350))
        self.Pack()
    
    def CreateMenu(self):
        """ Create menu bar """
        menuBar = wax.MenuBar(self)
        
        fileMenu = wax.Menu(self)
        fileMenu.Append(_("Open a new &tab"), self.OnNewTab, hotkey = "Ctrl-T")
        fileMenu.Append(_("&Close tab"), self.OnCloseTab, hotkey = "Ctrl-W")
        fileMenu.AppendSeparator()
        fileMenu.Append(_("&Save as"), self.OnSaveAs, hotkey = "Ctrl-S")
        fileMenu.Append(_("&Auto save"), self.OnAutoSave, hotkey = "Ctrl-Shift-S")
        fileMenu.AppendSeparator()
        fileMenu.Append(_("&Print"), self.OnPrint, hotkey = "Ctrl-P")
        fileMenu.AppendSeparator()
        fileMenu.Append(_("E&xit"), self.OnQuit, hotkey = "Ctrl-Q")
        
        helpMenu = wax.Menu(self)
        helpMenu.Append(_("&Help"), self.OnHelp, hotkey = "F1")
        helpMenu.AppendSeparator()
        helpMenu.Append(_("&About wxLyrics"), self.OnAbout)
        
        menuBar.Append(fileMenu, _("&File"))
        menuBar.Append(helpMenu, "&?")
    
    def OnQuit(self, event = None):
        """ Quit application """
        quitDialog = wax.MessageDialog(self, text = _("Do you really want to quit wxLyrics"), icon = "question", yes_no = 1)
        if quitDialog.ShowModal() == 'yes':
            self.Close(True)
            
    def OnNewTab(self, event = None):
        self._NewTab()
        
    def OnCloseTab(self, event = None):
        self._CloseTab()
        
    def OnSaveAs(self, event = None):
        """ Save lyrics in a text file. """
        if self.filename[self.currentTab]:
            self._SaveFile(self.filename[self.currentTab])
        else:
            saveDialog = wax.FileDialog(self, save = 1)
            try:
                if saveDialog.ShowModal() == 'ok':
                    filename = saveDialog.GetPath()
                    self.SetFilename(filename)
                    self._SaveFile(filename)
            finally:
                saveDialog.Destroy()
     
    def OnAutoSave(self, event = None):
        """ Save lyrics to a file depending on a model. """
        
        try:
            filePath = self._GenerateFilename(artist = self.result[self.currentTab]["artist"], song = self.result[self.currentTab]["song"],
                         album = self.result[self.currentTab]["album"])
            baseDir = os.path.expanduser(config.get('Output', 'BaseDir'))
            fullPath = os.path.join(baseDir, filePath)
            pathToFile = os.path.dirname(fullPath)
            
            if os.path.isdir(pathToFile) == False:
                os.makedirs(pathToFile, mode = 0755)
                
            self.SetFilename(fullPath)
            self._SaveFile(fullPath)
            
        except Exception, err:
            self.OnSaveAs()
    
    def OnPrint(self, event = None):
        """ Print lyrics. """
        
        self.currentTab = self.vPanel.noteBook.GetSelection()
        self.lyricsHTML = self._GenerateHTML("%s - %s" % (self.result[self.currentTab]["artist"], self.result[self.currentTab]["song"]),
                                 self.result[self.currentTab]["lyrics"])
        
        self.printer = Printer(self)
        self.printer.Print(self.lyricsHTML)
    
    def OnAbout(self, event = None):
        """ About dialog. """
        aboutDialog = AboutDialog(self, _("About wxLyrics"))
        aboutDialog.ShowModal()
        aboutDialog.Destroy()
    
    def OnHelp(self, event = None):
        """ Help dialog. """
        helpMessage = _("Fill the fields 'artist' and 'song title'. You will receive a list of song")
        helpFrame = wax.MessageDialog(self, _("Help"), helpMessage, ok = 1, icon = "information")
        helpFrame.ShowModal()
        helpFrame.Destroy()
        
    def OnSearch(self, event = None):
        """ Search lyrics and show them. """
        
        self.lyrics = {}
        
        # Get data from input
        input = self.vPanel.hPanelInput
        artist = input.artistInput.GetValue()
        song = input.songInput.GetValue()
        inputValidity = True
        
        # Verify fields
        if len(artist) < 3 and len(song) < 3:
            errorFrame = wax.MessageDialog(self, _("Error"), _("Fill required fields"), ok = 1, icon = "error")
            errorFrame.ShowModal()
            errorFrame.Destroy()
            inputValidity = False
            
        else:
            self.SetFilename(None)
            self.statusBar[1] = _("Searching")
            
            # Create a tab if needed
            self.currentTab = self.vPanel.noteBook.GetSelection()
            if self.usedTab[self.currentTab] == True: self._NewTab()
            
            self.vPanel.noteBook.tab[self.currentTab].lyricsText.Clear()
            self.vPanel.noteBook.tab[self.currentTab].lyricsText.InsertText(0, _("Seeking '%s' from %s ...") % (song, artist))
            
            # Search
            search = SearchLyrics()
            result = search.SearchLyrics(artist, song)
            
            self.vPanel.noteBook.tab[self.currentTab].lyricsText.Clear()
            
            # Detect errors
            try: self.error = result["error"]
            except Exception, err: self.error = False
            
            if self.error != False:
                errorFrame = wax.MessageDialog(self, _("Error"), self.error, ok = 1, icon = "error")
                errorFrame.ShowModal()
                errorFrame.Destroy()
            else:
                if len(result["songlist"].values()) == 0:
                    self.vPanel.noteBook.tab[self.currentTab].lyricsText.InsertText(0, _("No correspondence found"))
                    self.statusBar[1] = _("No correspondence found")
                    
                else:
                    songSelected = []
                    
                    # Song choice
                    if len(result["songlist"].values()) == 1:
                        songSelected = result["songlist"][0]
                    else:
                        i = 0
                        choices = {}
                        
                        for results in result["songlist"].values():
                            choices[i] = "%s - %s"  % (results[1], results[0])
                            i += 1
                            
                        choiceDialog = ChoiceDialog(self, choices = choices.values(), prompt = _("Make your choice"), title = _("Results"), size = (300, 200))
                        if choiceDialog.ShowModal() == 'ok':
                            songSelected = result["songlist"][choiceDialog.choice]
                        
                        choiceDialog.Destroy()
                    
                    # If the tuple didn't contain 3 fields, there's an error
                    if len(songSelected) != 3:
                        self.lyrics["error"] = _("No results")
                        self.vPanel.noteBook.tab[self.currentTab].lyricsText.Clear()
                        self.statusBar[1] = ""
                    else:
                        # Download lyrics
                        self.lyrics["artist"] = songSelected[0]
                        self.lyrics["song"] = songSelected[1]
                        self.lyrics["hid"] = songSelected[2]
                        
                        self.vPanel.noteBook.tab[self.currentTab].lyricsText.InsertText(0, _("Downloading '%s' ...") % self.lyrics["song"])
                        
                        self.lyrics["lyrics"] = search.ShowLyrics(self.lyrics["hid"])
                     
                        # Detect errors
                        try: self.error = self.lyrics["lyrics"]["error"]
                        except Exception, err: self.error = False
                        
                        if self.error != False:
                            errorFrame = wax.MessageDialog(self, _("Error"), self.lyrics["lyrics"]["error"], ok = 1, icon = "error")
                            errorFrame.ShowModal()
                            errorFrame.Destroy()
                            self.statusBar[1] = self.lyrics["lyrics"]["error"]
                        else:
                            self.vPanel.noteBook.tab[self.currentTab].lyricsText.Clear()
                            self.vPanel.noteBook.tab[self.currentTab].lyricsText.InsertText(0, self.lyrics["lyrics"]["lyrics"])
                            self.vPanel.noteBook.tab[self.currentTab].lyricsText.InsertText(0, "[%s - %s]\r\r" % (self.lyrics["artist"], self.lyrics["song"]))
                            self.vPanel.noteBook.SetPageText(self.currentTab, "%s - %s" % (self.lyrics["artist"], self.lyrics["song"]))
                            self.statusBar[1] = self.lyrics["artist"] + " - " + self.lyrics["song"]
                            self.usedTab[self.currentTab] = True
                            self.result[self.currentTab] = {'artist': self.lyrics["artist"], 'song': self.lyrics["song"],
                                                                        'album': self.lyrics["lyrics"]["album"], 'lyrics': self.lyrics["lyrics"]["lyrics"]}
    
    def _NewTab(self, movingon = True):
        """ Create new tab and moves on if precedent tab is used or not. """
        
        tabNumber = len(self.vPanel.noteBook.tab)
        self.filename.append(None)
        self.usedTab.append(False)
        self.result.append(None)
        self.vPanel.noteBook.tab.append(wax.Panel(self.vPanel.noteBook))
        self.vPanel.noteBook.tab[tabNumber].lyricsText = wax.TextBox(self.vPanel.noteBook.tab[tabNumber], multiline=1, Value = _("Lyrics"))
        self.vPanel.noteBook.tab[tabNumber].AddComponent(self.vPanel.noteBook.tab[tabNumber].lyricsText, expand = 'both')
        
        self.vPanel.noteBook.AddPage(self.vPanel.noteBook.tab[tabNumber], _("Untitled %s") % (int(tabNumber) + 1))
        self.vPanel.noteBook.tab[tabNumber].Pack()
        
        # Move on new tab
        if movingon == True and self.usedTab[self.vPanel.noteBook.GetSelection()] == True:
            self.vPanel.noteBook.SetSelection(tabNumber)
            self.currentTab = self.vPanel.noteBook.GetSelection()
    
    def _CloseTab(self):
        """ Delete current tab. """
        
        currentTab = self.currentTab
        
        if self.vPanel.noteBook.GetPageCount() == 1:
            self.vPanel.noteBook.tab[0].lyricsText.Clear()
            self.vPanel.noteBook.tab[0].lyricsText.InsertText(0, _("Lyrics"))
            self.vPanel.noteBook.SetPageText(0, _("Untitled %s") % 1)
            self.result[0] = None
            self.filename[0] = None
            self.currentTab = 1
        else:
            try:
                if self.usedTab[currentTab + 1] == True:
                    self.usedTab[currentTab] = True
                else:
                    self.usedTab[currentTab] = False
            except Exception, err:
                self.usedTab[currentTab] = False
                
            self.vPanel.noteBook.RemovePage(currentTab)
            self.result.remove(self.result[self.currentTab])
            self.filename.remove(self.filename[self.currentTab])
            self.vPanel.noteBook.tab.remove(self.vPanel.noteBook.tab[currentTab])
            self.currentTab = currentTab - 1
    
    def _GenerateHTML(self, header, content):
        """ Generate HTML code. """
        
        HTML = "<h3 align=\"center\">%s</h3><br><br><span style=\"font-size: 10pt\">%s</span>" % (header, content)
        
        return HTML.encode('latin-1', 'replace').replace('\n', '<br>')
    
    def _SaveFile(self, filename):
        """ Save lyrics in text file """
        filename = open(filename, 'w')
        filename.write(self.vPanel.noteBook.tab[0].lyricsText.GetValue().encode('latin-1', 'replace'))
        filename.close()
        
    def _GenerateFilename(self, *args, **kwds):
        """ Genrate filename from a model. """
        
        filename = [config.get("Output", "Model")]
        filename.append(filename[0].replace('%artist', kwds["artist"]))
        filename.append(filename[1].replace('%song', kwds["song"]))
        filename.append(filename[2].replace('%album', kwds["album"]))
        
        return filename[-1]
    
    def SetFilename(self, filename):
        self.filename[self.currentTab] = filename
        self.statusBar[0] = str(self.filename[self.currentTab])

class AboutDialog(wax.CustomDialog):
    """ Create About window. """
    
    def Body(self):
        import platform
        
        # Create dialog
        programName = wax.Label(self, "wxLyrics %s" % config.get('Program', 'Version'))
        programName.SetFont(('Verdana', 14))
        noteBook = wax.NoteBook(self, size = (400,300))
        closeButton = wax.Button(self, "Fermer", event = self.OnQuit)
        
        # About tab
        aboutTab = wax.Panel(noteBook)
        
        aboutTab.copyrightText = _("wxLyrics - A simple lyrics viewer")
        aboutTab.copyrightText += "\n(c) 2006, Svoboda Vladimir"
        aboutTab.copyrightText += "\n<ze.vlad@gmail.com>\n"
        aboutTab.copyrightText += _("Lyrics provided by %s.") % "http://www.lesolyrics.com"
        
        aboutTab.copyright = wax.Label(aboutTab, aboutTab.copyrightText)
        aboutTab.AddComponent(aboutTab.copyright, border = 10)
        aboutTab.Pack()
        noteBook.AddPage(aboutTab, _("About"))
        
        # License tab
        licenceTab = wax.Panel(noteBook)
        licenceTab.file = open('COPYING', 'r')
        licenceTab.text = wax.TextBox(licenceTab, multiline = 1, Value = licenceTab.file.read())
        licenceTab.text.SetEditable(False)
        licenceTab.AddComponent(licenceTab.text, expand = 'both', border = 5)
        licenceTab.Pack()
        noteBook.AddPage(licenceTab, _("License"))
        
        # Informations tab
        infoTab = wax.Panel(noteBook)
        
        infoTab.infoText = _("System: %s") % platform.platform()
        infoTab.infoText += "\nPython: %s\nwxPython: %s" % (platform.python_version(), wx.VERSION_STRING)
        
        infoTab.info = wax.Label(infoTab, infoTab.infoText)
        infoTab.AddComponent(infoTab.info, border = 10)
        infoTab.Pack()
        noteBook.AddPage(infoTab, _("Informations"))
        
        # Window settings
        self.AddComponent(programName)
        self.AddSpace(10)
        self.AddComponent(noteBook, expand = 'both')
        self.AddComponent(closeButton, border = 3, align = 'center')
        self.Pack()
    
    def OnQuit(self, event = None):
        self.Close()
        
if __name__ == "__main__":
    # Configuration file
    configFile = os.path.join(os.getcwd(), "wxlyrics.cfg")
    config = ConfigParser.ConfigParser()
    config.readfp(open(configFile, 'r'))
    
    # Gettext init
    gettext.bindtextdomain("wxlyrics")
    locale.setlocale(locale.LC_ALL,'')
    gettext.textdomain("wxlyrics")
    gettext.install("wxlyrics",localedir = config.get("Locale", "Dir"), unicode = 1)
    
    # Creates windows
    wxLyrics = wax.Application(MainFrame, title = "wxLyrics")
    wxLyrics.Run()