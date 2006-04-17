#
#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
#

#	Programmer: Svoboda Vladimir
#	E-mail: ze.vlad@gmail.com
#
#	Copyright 2006 Svoboda Vladimir
#
#	Distributed under the terms of the GPL (GNU Public License)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
#	Requirements (Dependencies): wxPython and waxgui.

import sys, os
import locale, gettext, ConfigParser
import wax, wx.html
from wax.tools.choicedialog import ChoiceDialog
from searchlyrics import SearchLyrics


def GenerateHTML(header, content):
    """ Generate HTML code. """
    
    HTML = "<h3 align=\"center\">%s</h3><br><br><span style=\"font-size: 10pt\">%s</span>" % (header, content)
    
    return HTML.encode('latin-1', 'replace').replace('\n', '<br>')

def GenerateFilename(*args, **kwds):
    """ Generate filename from a model. """
    
    filename = [config.get("Output", "Model")]
    filename.append(filename[0].replace('%artist', kwds['artist']))
    filename.append(filename[1].replace('%song', kwds['song']))
    filename.append(filename[2].replace('%album', kwds['album']))
    
    return filename[-1]

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
        self.Pack()
        self.Size = (450, 350)
        
        self.vPanel.noteBook.OnPageChanged  = self.OnTabChange
    
    def CreateMenu(self):
        """ Create menu bar """
        menuBar = wax.MenuBar(self)
        
        fileMenu = wax.Menu(self)
        fileMenu.Append(_("Open new &tab"), self.OnNewTab, hotkey = "Ctrl-T")
        fileMenu.Append(_("&Close tab"), self.OnCloseTab, hotkey = "Ctrl-W")
        fileMenu.AppendSeparator()
        fileMenu.Append(_("&Save as"), self.OnSaveAs, hotkey = "Ctrl-S")
        fileMenu.Append(_("&Auto save"), self.OnAutoSave, hotkey = "Ctrl-Shift-S")
        fileMenu.AppendSeparator()
        fileMenu.Append(_("&Print"), self.OnPrint, hotkey = "Ctrl-P")
        fileMenu.AppendSeparator()
        fileMenu.Append(_("E&xit"), self.OnQuit, hotkey = "Ctrl-Q")
        
        editMenu = wax.Menu(self)
        editMenu.Append(_("&Preferences"), self.OnPreferences)
        
        helpMenu = wax.Menu(self)
        helpMenu.Append(_("&Help"), self.OnHelp, hotkey = "F1")
        helpMenu.AppendSeparator()
        helpMenu.Append(_("&About wxLyrics"), self.OnAbout)
        
        menuBar.Append(fileMenu, _("&File"))
        menuBar.Append(editMenu, _("&Edit"))
        menuBar.Append(helpMenu, "&?")
    
    def OnQuit(self, event = None):
        """ Quit application """
        quitDialog = wax.MessageDialog(self, text = _("Do you really want to quit wxLyrics"), icon = "question", yes_no = 1)
        if quitDialog.ShowModal() == 'yes':
            self.Close(True)
            
    def OnTabChange(self, event):
        self.currentTab = event.GetSelection()
        self.statusBar[0] = str(self.filename[self.currentTab])
        event.Skip()
    
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
            filePath = GenerateFilename(artist = self.result[self.currentTab]['artist'], song = self.result[self.currentTab]['song'],
                         album = self.result[self.currentTab]['album'])
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
        
        self.lyricsHTML = GenerateHTML("%s - %s" % (self.result[self.currentTab]['artist'], self.result[self.currentTab]['song']),
                                 self.result[self.currentTab]['lyrics'])
        
        self.printer = Printer(self)
        self.printer.Print(self.lyricsHTML)
    
    def OnPreferences(self, event = None):
        """ Preferences dialog. """
        prefDialog = PreferencesDialog(self, _("Preferences"))
        prefDialog.ShowModal()
        prefDialog.Destroy()
    
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
        print "Recherche: ", self.currentTab
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
            if self.usedTab[self.currentTab] == True: self._NewTab()
            print "Recherche 2: ", self.currentTab
            self.vPanel.noteBook.tab[self.currentTab].lyricsText.Clear()
            self.vPanel.noteBook.tab[self.currentTab].lyricsText.InsertText(0, _("Seeking '%s' from %s ...") % (song, artist))
            
            # Search
            search = SearchLyrics()
            result = search.SearchLyrics(artist, song)
            
            self.vPanel.noteBook.tab[self.currentTab].lyricsText.Clear()
            
            # Detect errors
            try: self.error = result['error']
            except Exception, err: self.error = False
            
            if self.error != False:
                errorFrame = wax.MessageDialog(self, _("Error"), self.error, ok = 1, icon = "error")
                errorFrame.ShowModal()
                errorFrame.Destroy()
            else:
                if len(result['songlist'].values()) == 0:
                    self.vPanel.noteBook.tab[self.currentTab].lyricsText.InsertText(0, _("No correspondence found"))
                    self.statusBar[1] = _("No correspondence found")
                    
                else:
                    songSelected = []
                    
                    # Song choice
                    if len(result['songlist'].values()) == 1:
                        songSelected = result['songlist'][0]
                    else:
                        i = 0
                        choices = {}
                        
                        for results in result['songlist'].values():
                            choices[i] = "%s - %s"  % (results[1], results[0])
                            i += 1
                            
                        choiceDialog = ChoiceDialog(self, choices = choices.values(), prompt = _("Make your choice"), title = _("Results"), size = (300, 200))
                        if choiceDialog.ShowModal() == 'ok':
                            songSelected = result['songlist'][choiceDialog.choice]
                        
                        choiceDialog.Destroy()
                    
                    # If tuple didn't contain 3 fields, there's an error
                    if len(songSelected) != 3:
                        self.lyrics['error'] = _("No results")
                        self.vPanel.noteBook.tab[self.currentTab].lyricsText.Clear()
                        self.statusBar[1] = ""
                    else:
                        # Download lyrics
                        self.lyrics['artist'] = songSelected[0]
                        self.lyrics['song'] = songSelected[1]
                        self.lyrics['hid'] = songSelected[2]
                        
                        self.vPanel.noteBook.tab[self.currentTab].lyricsText.InsertText(0, _("Downloading '%s' ...") % self.lyrics['song'])
                        
                        self.lyrics['lyrics'] = search.ShowLyrics(self.lyrics['hid'])
                     
                        # Detect errors
                        try: self.error = self.lyrics['lyrics']['error']
                        except Exception, err: self.error = False
                        
                        if self.error != False:
                            errorFrame = wax.MessageDialog(self, _("Error"), self.lyrics['lyrics']['error'], ok = 1, icon = "error")
                            errorFrame.ShowModal()
                            errorFrame.Destroy()
                            self.statusBar[1] = self.lyrics['lyrics']['error']
                        else:
                            self.vPanel.noteBook.tab[self.currentTab].lyricsText.Clear()
                            self.vPanel.noteBook.tab[self.currentTab].lyricsText.InsertText(0, self.lyrics['lyrics']['lyrics'])
                            self.vPanel.noteBook.tab[self.currentTab].lyricsText.InsertText(0, "[%s - %s]\r\r" % (self.lyrics['artist'], self.lyrics['song']))
                            self.vPanel.noteBook.SetPageText(self.currentTab, "%s - %s" % (self.lyrics['artist'], self.lyrics['song']))
                            self.statusBar[1] = self.lyrics['artist'] + " - " + self.lyrics['song']
                            self.usedTab[self.currentTab] = True
                            self.result[self.currentTab] = {'artist': self.lyrics['artist'], 'song': self.lyrics['song'],
                                                                        'album': self.lyrics['lyrics']['album'], 'lyrics': self.lyrics['lyrics']['lyrics']}
    
    def _NewTab(self, movingon = True):
        """ Create new tab and moves on, if precedent tab is used or not. """
        
        tabNumber = self.vPanel.noteBook.GetPageCount()
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
    
    def _CloseTab(self):
        """ Delete current tab. """
        
        if self.vPanel.noteBook.GetPageCount() == 1:
            self.vPanel.noteBook.tab[0].lyricsText.Clear()
            self.vPanel.noteBook.tab[0].lyricsText.InsertText(0, _("Lyrics"))
            self.vPanel.noteBook.SetPageText(0, _("Untitled %s") % 1)
            self.result = [None]
            self.filename = [None]
        else:
            try:
                if self.usedTab[self.currentTab + 1] == True:
                    self.usedTab[self.currentTab] = True
                else:
                    self.usedTab[self.currentTab] = False
            except Exception, err:
                self.usedTab[self.currentTab] = False
                
            self.vPanel.noteBook.RemovePage(self.currentTab)
            self.result.remove(self.result[self.currentTab])
            self.filename.remove(self.filename[self.currentTab])
            self.vPanel.noteBook.tab.remove(self.vPanel.noteBook.tab[self.currentTab])
    
    def _SaveFile(self, filename):
        """ Save lyrics in text file """
        
        if not self.result[self.currentTab]['artist']:
            errorFrame = wax.MessageDialog(self, _("Error"), _("Nothing to save"), ok = 1, icon = "error")
            errorFrame.ShowModal()
            errorFrame.Destroy()
            
        else:
            try:
                filename = open(filename, 'w')
                filename.write(self.vPanel.noteBook.tab[0].lyricsText.GetValue().encode('latin-1', 'replace'))
                filename.close()
            except Exception, err:
                print err
                errorFrame = wax.MessageDialog(self, _("Error"), _("Saving failed"), ok = 1, icon = "error")
                errorFrame.ShowModal()
                errorFrame.Destroy()
    
    def SetFilename(self, filename):
        self.filename[self.currentTab] = filename
        self.statusBar[0] = str(self.filename[self.currentTab])

class PreferencesDialog(wax.CustomDialog):
    """ Create Preferences window. """
    
    def Body(self):
        gPanel = wax.GridPanel(self, rows = 3, cols = 2, hgap = 0, vgap = 5)
        
        self.baseDir = wax.TextBox(gPanel, Value = os.path.expanduser(config.get('Output', 'BaseDir')))
        self.fileModel = wax.TextBox(gPanel, Value = config.get('Output', 'Model'))
        self.fileExample = wax.Label(gPanel, GenerateFilename(artist = 'Manau', song = 'Dafunkamanu', album = 'Fest Noz De Paname'))
        
        gPanel.AddComponent(0, 0, wax.Label(gPanel, _("Output directory")))
        gPanel.AddComponent(0, 1, wax.Label(gPanel, _("File model")))
        gPanel.AddComponent(0, 2, wax.Label(gPanel, _("Example")))
        gPanel.AddComponent(1, 0, self.baseDir)
        gPanel.AddComponent(1, 1, self.fileModel)
        gPanel.AddComponent(1, 2, self.fileExample)
        gPanel.Pack()
        
        self.AddComponent(wax.Label(self, _("Global preferences")))
        self.AddComponent(gPanel, expand = 'both', border = 10)
        self.AddComponent(wax.Button(self, _("Close"), event = self.OnQuit), border = 3, align = 'center')
        self.AddComponent(wax.Button(self, _("Ok"), event = self.OnOk), border = 3, align = 'center')
        self.AddComponent(wax.Button(self, _("Obort"), event = self.OnAbort), border = 3, align = 'center')
        self.Pack()
        self.Size = (400, 200)
        
    def OnQuit(self, event = None):
        self.Close()
    
    def OnQuit(self, event = None):
        print "Save config"
        
    def OnAbort(self, event = None):
        print "Aborting"
        
class AboutDialog(wax.CustomDialog):
    """ Create About window. """
    
    def Body(self):
        import platform
        
        # Create dialog
        programName = wax.Label(self, "wxLyrics %s" % config.get('Program', 'Version'))
        programName.SetFont(('Verdana', 14))
        noteBook = wax.NoteBook(self, size = (400,300))
        
        # About tab
        aboutTab = wax.Panel(noteBook)
        
        aboutTab.copyrightText = _("wxLyrics - A simple lyrics viewer")
        aboutTab.copyrightText += "\n(c) 2006, Svoboda Vladimir"
        aboutTab.copyrightText += "\n<ze.vlad@gmail.com>\n"
        aboutTab.copyrightText += _("Lyrics provided by %s") % "leoslyrics"
        
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
        self.AddComponent(wax.Button(self, _("Close"), event = self.OnQuit), border = 3, align = 'center')
        self.Pack()
    
    def OnQuit(self, event = None):
        self.Close()
        
if __name__ == "__main__":
    # Configuration file
    configFile = os.path.join(os.path.abspath('wxlyrics.cfg'))
    config = ConfigParser.ConfigParser()
    config.readfp(open(configFile, 'r'))
    
    # Gettext init
    gettext.bindtextdomain('wxlyrics')
    locale.setlocale(locale.LC_ALL, '')
    gettext.textdomain('wxlyrics')
    gettext.install('wxlyrics', os.path.abspath('locales'), unicode = 1)
    
    # Creates windows
    wxLyrics = wax.Application(MainFrame, title = "wxLyrics")
    wxLyrics.Run()