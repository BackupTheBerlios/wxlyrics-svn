#
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# Programmer: Svoboda Vladimir
# E-mail: ze.vlad@gmail.com
#
# 2006 Svoboda Vladimir
#
# Distributed under the terms of the GPL (GNU Public License)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
# Requirements (Dependencies): wxPython and waxgui.
#
# $Id$

__version__ = '0.1.0524'

import sys
import os
import locale
import gettext
import ConfigParser

from wax import *
from wax.tools.choicedialog import ChoiceDialog
import wx.html

from searchlyrics import SearchLyrics


def GenerateHTML(header, content):
    """ Generate HTML code. """
    
    HTML = "<h3 align=\"center\">%s</h3><br><br> \
            <span style=\"font-size: 10pt\">%s</span>" % (header, content)
    
    return HTML.encode('latin-1', 'replace').replace('\n', '<br>')

def GenerateFilename(*args, **kwds):
    """ Generate filename from a model. """
    
    if kwds.has_key('model'):
        filename = [kwds['model']]
    else:
        filename = [config.get('Output', 'Model')]
        
    filename.append(filename[0].replace('%artist', kwds['artist']))
    filename.append(filename[1].replace('%song', kwds['song']))
    filename.append(filename[2].replace('%album', kwds['album']))
    
    return filename[-1]

class Printer(wx.html.HtmlEasyPrinting):
    """ Prints HTML code. """
    
    def __init__(self, parent):
        wx.html.HtmlEasyPrinting.__init__(self)
        self.parent = parent
        
    def Print(self, text, linenumbers=1):
        self.PrintText(text)

class MainFrame(Frame):
    """ Main window with menu, status bar and notebook (tabs) for lyrics. """
    
    def Body(self):
        # Create status bar
        self.statusBar = StatusBar(self, numpanels=3)
        self.SetStatusBar(self.statusBar)
        
        # Create menu and body
        self.LyricsCowMenu()
        self.lyricsCow = self.LyricsCowBody()
        #self.SetIcon('lyricistCow.ico')
        self.SetSize((400, 400))
        
    def CommonMenu(self):
        """ Create menu bar """
        self.menuBar = MenuBar(self)
        
        editMenu = Menu(self)
        editMenu.Append(_("Search mode"), self.CreateLyricsCow, type='radio')
        editMenu.Append(_("Library completing mode"), self.CreatePodCow, type='radio')
        editMenu.AppendSeparator()
        editMenu.Append(_("&Preferences"), self.OnPreferences)
        
        helpMenu = Menu(self)
        helpMenu.Append(_("&Help"), self.OnHelp, hotkey = "F1")
        helpMenu.AppendSeparator()
        helpMenu.Append(_("&About The Musical Cow"), self.OnAbout)
        
        self.menuBar.Append(editMenu, _("&Edit"))
        self.menuBar.Append(helpMenu, _("&?"))
        
    
    def LyricsCowMenu(self):
        """ Create menu bar """
        self.CommonMenu()
        
        fileMenu = Menu(self)
        fileMenu.Append(_("Open new &tab"), self._NewTab, hotkey = "Ctrl-T")
        fileMenu.Append(_("&Close tab"), self._CloseTab, hotkey = "Ctrl-W")
        fileMenu.AppendSeparator()
        fileMenu.Append(_("&Save as"), self.OnSaveAs, hotkey = "Ctrl-S")
        fileMenu.Append(_("&Auto save"), self.OnAutoSave, hotkey = "Ctrl-Shift-S")
        fileMenu.AppendSeparator()
        fileMenu.Append(_("&Print"), self.OnPrint, hotkey = "Ctrl-P")
        fileMenu.AppendSeparator()
        fileMenu.Append(_("E&xit"), self.OnQuit, hotkey = "Ctrl-Q")
        
        self.menuBar.Insert(0, fileMenu, _("&File"))
  
    def PodCowMenu(self):
        """ Create menu bar """
        self.CommonMenu()
        
        fileMenu = Menu(self)
        fileMenu.Append(_("E&xit"), self.OnQuit, hotkey = "Ctrl-Q")
        
        self.menuBar.Insert(0, fileMenu, _("&File"))
    
    def CreateLyricsCow(self, event=None):
        """ Switch to searching mode. """
        
        # Destroy old panel; create a new one; repack
        self.podCow.Destroy()
        self.lyricsCow = self.LyricsCowBody()
        self.LyricsCowMenu()
        self.Repack()
        
        self.SetSizeX(self.GetSizeX()+1)
    
    def CreatePodCow(self, event=None):
        """ Switch to library tagging mode. """
        
        # Destroy old panel; create a new one; repack
        self.lyricsCow.Destroy()
        self.lyricsCow = None
        self.podCow = self.PodCowBody()
        self.PodCowMenu()
        self.Repack()
     
        self.SetSizeX(self.GetSizeX()+1)
        
    def _NewTab(self, event=None, movingon=True):
        """ Create new tab and moves on, if precedent tab is used or not. """
        
        tabNumber = self.nb.GetPageCount()
        self.filename.append(None)
        self.usedTab.append(False)
        self.result.append(None)
        self.nb.tab.append(Panel(self.nb))
        self.nb.tab[tabNumber].lyricsText = TextBox(self.nb.tab[tabNumber], multiline=1, Value=_("Lyrics"))
        self.nb.tab[tabNumber].AddComponent(self.nb.tab[tabNumber].lyricsText, expand='both')
        self.nb.AddPage(self.nb.tab[tabNumber], _("Untitled %s") % (int(tabNumber) + 1))
        self.nb.tab[tabNumber].Pack()
        
        if movingon == True and self.usedTab[self.nb.GetSelection()] == True:
            self.nb.SetSelection(tabNumber)
    
    def _CloseTab(self, movingon=True):
        """ Delete current tab. """
        
        if self.nb.GetPageCount() == 1:
            self.nb.tab[0].lyricsText.Clear()
            self.nb.tab[0].lyricsText.InsertText(0, _("Lyrics"))
            self.nb.SetPageText(0, _("Untitled %s") % 1)
            self.result = [None]
            self.filename = [None]
        else:
            try:
                if self.usedTab[self.cTab + 1] == True:
                    self.usedTab[self.cTab] = True
                else:
                    self.usedTab[self.cTab] = False
            except Exception, err:
                self.usedTab[self.cTab] = False
                
            self.nb.RemovePage(self.cTab)
            self.result.remove(self.result[self.cTab])
            self.filename.remove(self.filename[self.cTab])
            self.nb.tab.remove(self.nb.tab[self.cTab])
            self.cTab = self.nb.GetSelection()
    
    def LyricsCowBody(self, event=None):
        self.result = [None]
        self.filename = [None]
        lyricsCow = VerticalPanel(self)
        
        # Buttons
        self.input = HorizontalPanel(lyricsCow)
        
        self.input.artist = TextBox(self.input, _("Artist"))
        self.input.song = TextBox(self.input, _("Song title"))
        self.input.search = Button(self.input, _("Search"), event=self.OnSearch)
        
        self.input.AddComponent(self.input.artist, border=5)
        self.input.AddComponent(self.input.song, border=5)
        self.input.AddComponent(self.input.search, border=5)
        self.input.Pack()
        
        # nb
        self.nb = NoteBook(lyricsCow, size = (400, 300))
        self.nb.tab = [Panel(self.nb)]
        
        # Tabs
        self.usedTab = [False]
        self.cTab = 0  # Current tab, will change after tab changing
        self.nb.OnPageChanged  = self.OnTabChange
        
        self.nb.tab[0].lyricsText = TextBox(self.nb.tab[0], multiline=1,
                                            Value=_("Lyrics"))
        self.nb.tab[0].AddComponent(self.nb.tab[0].lyricsText, expand='both')
        self.nb.AddPage(self.nb.tab[0], _("Untitled %s") % 1)
        self.nb.tab[0].Pack()
        
        lyricsCow.AddComponent(self.input, border=5)
        lyricsCow.AddComponent(self.nb, expand = 'both')
        
        # Window Settings
        lyricsCow.Pack()
        self.AddComponent(lyricsCow, expand='both')
        
        return lyricsCow
    
    def PodCowBody(self):
        podCow = VerticalPanel(self)
        
        error = None
        self.result = [None]
        self.filename = [None]
        
        gPanel = HorizontalPanel(podCow)
        
        self.musicPath = TextBox(gPanel,
                                 Value=config.get('MusicRoot', 'directory'))
        
        gPanel.AddComponent(Label(gPanel, _("Music Directory:"), align='right'),
                                  border=8)
        gPanel.AddComponent(self.musicPath, expand='h', border=5)
        gPanel.AddComponent(Button(gPanel, _("Browse"), self.Browse), border=5)
        gPanel.Pack()
        
        buttonPanel = HorizontalPanel(podCow)
        scan = Button(buttonPanel, _("Scan"), event=self.OnAnalyze)
        add = Button(buttonPanel, _("Add lyrics"), event=self.OnAddLyrics)
        buttonPanel.AddComponent(scan, border=5, align='center')
        buttonPanel.AddComponent(add, border=5, align='center')
        buttonPanel.Pack()
        
        podCow.AddComponent(gPanel, expand='h', border=5)
        podCow.AddComponent(buttonPanel, border=5, align='center')
        self.output = TextBox(podCow, multiline=1)
        podCow.AddComponent(self.output, expand='both')
        
        podCow.Pack()
        self.AddComponent(podCow, expand='both')
        
        return podCow
    
    def OnQuit(self, event=None):
        """ Quit application """
        quitDialog = MessageDialog(self,
                               text=_("Do you really want to quit lyricistCow"),
                               icon = "question", yes_no = 1)
        if quitDialog.ShowModal() == 'yes':
            self.Close(True)
            
    def OnTabChange(self, event=None):
        """ Refresh some variable after every tab changing. """
        self.cTab = event.GetSelection()
        self.SetFilename(self.filename[self.cTab])
        self.statusBar[1] = self.nb.GetPageText(self.cTab)
        event.Skip()
        self.SetSizeX(self.GetSizeX()+1)
        
    def OnSaveAs(self, event=None):
        """ Save lyrics in a text file. """
        if self.filename[self.cTab]:
            self._SaveFile(self.filename[self.cTab])
        else:
            saveDialog = FileDialog(self, save = 1)
            try:
                if saveDialog.ShowModal() == 'ok':
                    filename = saveDialog.GetPath()
                    self.SetFilename(filename)
                    self._SaveFile(filename)
            finally:
                saveDialog.Destroy()
     
    def OnAutoSave(self, event=None):
        """ Save lyrics to a file depending on a model. """
        
        try:
            filePath = GenerateFilename(artist=self.result[self.cTab]['artist'],
                                        song=self.result[self.cTab]['song'],
                                        album=self.result[self.cTab]['album'])
            baseDir = os.path.expanduser(config.get('Output', 'BaseDir'))
            fullPath = os.path.join(baseDir, filePath)
            pathToFile = os.path.dirname(fullPath)
            
            if os.path.isdir(pathToFile) == False:
                os.makedirs(pathToFile, mode=0755)
                
            self.SetFilename(fullPath)
            self._SaveFile(fullPath)
            
        except Exception, err:
            self.OnSaveAs()
    
    def OnPrint(self, event=None):
        """ Print lyrics. """
        
        self.lyricsHTML = GenerateHTML("%s - %s" %
                                       (self.result[self.cTab]['artist'],
                                        self.result[self.cTab]['song']),
                                       self.result[self.cTab]['lyrics'])
        
        self.printer = Printer(self)
        self.printer.Print(self.lyricsHTML)
    
    def OnPreferences(self, event=None):
        """ Preferences dialog. """
        
        prefDialog = PreferencesDialog(self, _("Preferences"))
        prefDialog.ShowModal()
        prefDialog.Destroy()
    
    def OnAbout(self, event=None):
        """ About dialog. """
        
        aboutDialog = AboutDialog(self, _("About lyricistCow"))
        aboutDialog.ShowModal()
        aboutDialog.Destroy()
    
    def OnHelp(self, event=None):
        """ Help dialog. """
        
        helpMessage = _("Fill the fields 'artist' and 'song title' and "
                        "you will receive a list of song")
        helpFrame = MessageDialog(self, _("Help"), helpMessage, ok=1,
                                      icon='information')
        helpFrame.ShowModal()
        helpFrame.Destroy()
    
    def OnSearch(self, event=None):
        """ Search lyrics and show them. """
        
        self.lyrics = {}
        # Get data from input
        input = self.input
        artist = input.artist.GetValue()
        song = input.song.GetValue()
        
        # Verify fields
        if len(artist) < 3 and len(song) < 3:
            errorFrame = MessageDialog(self, _("Error"),
                                       _("Fill the required fields"), ok=1,
                                       icon='error')
            errorFrame.ShowModal()
            errorFrame.Destroy()
            return
            
        self.SetFilename(None)
        self.statusBar[1] = _("Searching")
        
        # Create a tab if needed
        if self.usedTab[self.cTab] == True: self._NewTab()
           
        self.nb.tab[self.cTab].lyricsText.Clear()
        self.nb.tab[self.cTab].lyricsText.InsertText(0,
                                _("Seeking '%s' from %s ...") % (song, artist))
            
        # Search
        search = SearchLyrics()
        result = search.SearchLyrics(artist, song)
        
        self.nb.tab[self.cTab].lyricsText.Clear()
        
        # Detect errors
        if result.has_key('error'):
            self.error = result['error']
            errorFrame = MessageDialog(self, _("Error"), self.error, ok = 1,
                                       icon = "error")
            errorFrame.ShowModal()
            errorFrame.Destroy()
            return
      
        if len(result['songlist']) == 0:
            self.nb.tab[self.cTab].lyricsText.InsertText(0,
                                           _("No correspondence found"))
            self.statusBar[1] = _("No correspondence found")
                
        else:
            songSelected = []
            
            # Song choice
            if len(result['songlist'].values()) == 1:
                songSelected = result['songlist'][0]
            else:
                choices = []
                
                for results in result['songlist'].values():
                    choices.append("%s - %s"  % (results[1], results[0]))
                    
                choiceDialog = ChoiceDialog(self, choices = choices,
                                                    prompt = _("Make your choice"),
                                                    title = _("Results"),
                                                    size = (300, 200))
                if choiceDialog.ShowModal() == 'ok':
                    songSelected = result['songlist'][choiceDialog.choice]
                
                choiceDialog.Destroy()
            
            # Download lyrics
            self.lyrics['artist'] = songSelected[0]
            self.lyrics['song'] = songSelected[1]
            self.lyrics['hid'] = songSelected[2]
            
            self.nb.tab[self.cTab].lyricsText.InsertText(0, _("Downloading '%s' ...") % self.lyrics['song'])
            self.lyrics['lyrics'] = search.ShowLyrics(self.lyrics['hid'])
                     
            # Detect errors
            if self.lyrics['lyrics'].has_key('error'):
                self.error = self.lyrics['lyrics']['error']
                errorFrame = MessageDialog(self, _("Error"), self.error, ok = 1, icon = "error")
                errorFrame.ShowModal()
                errorFrame.Destroy()
                self.statusBar[1] = self.error
                return
            
            self.nb.tab[self.cTab].lyricsText.Clear()
            self.nb.tab[self.cTab].lyricsText.InsertText(0, self.lyrics['lyrics']['lyrics'])
            self.nb.tab[self.cTab].lyricsText.InsertText(0, "[%s - %s]\r\r" % (self.lyrics['artist'], self.lyrics['song']))
            self.nb.SetPageText(self.cTab, "%s - %s" % (self.lyrics['artist'], self.lyrics['song']))
            self.statusBar[1] = self.lyrics['artist'] + " - " + self.lyrics['song']
            self.usedTab[self.cTab] = True
            self.result[self.cTab] = {'artist': self.lyrics['artist'], 'song': self.lyrics['song'],
                                       'album': self.lyrics['lyrics']['album'], 'lyrics': self.lyrics['lyrics']['lyrics']}

    
    def _SaveFile(self, filename):
        """ Save lyrics in text file """
        
        if not self.result[self.cTab]['artist']:
            errorFrame = MessageDialog(self, _("Error"), _("Nothing to save"), ok = 1, icon = "error")
            errorFrame.ShowModal()
            errorFrame.Destroy()
            
        else:
            try:
                filename = open(filename, 'w')
                filename.write(self.nb.tab[self.cTab].lyricsText.GetValue().encode('latin-1', 'replace'))
                filename.close()
            except Exception, err:
                errorFrame = MessageDialog(self, _("Error"), _("Saving failed"), ok = 1, icon = "error")
                errorFrame.ShowModal()
                errorFrame.Destroy()
    
    def SetFilename(self, filename):
        self.filename[self.cTab] = filename
        self.statusBar[0] = str(self.filename[self.cTab])
    
    def OnAnalyze(self, event=None):
        self.fileList, self.fileNumber, self.mTags = self.Analyze(self.musicPath.GetValue())
    
    def OnAddLyrics(self, event=None):
        dlg = ProgressDialog(self, title=_("Add lyrics into audio file"),
        message=_("Add lyrics to the %d files") % self.mTags, maximum=self.mTags,
        abort=1)
        dlg.Show()
        cancel = True
        added = 0
        self.statusBar[2] = _("Tags added: %s") % 0
        
        for i in range(self.mTags):
            lyrics = {}
            songSelected = {}
            
            audio = ID3(self.fileList[i][0])
            artist = str(audio.getall('TPE1')[0])
            song = str(audio.getall('TIT2')[0])
            
            cancel = dlg.Update(i, _("Adding lyrics to %s - %s") % (artist, song))
            
            search = SearchLyrics()
            result = search.SearchLyrics(artist, song)
            
            if result.has_key('error'):
                self.output.InsertText(0, _("ERROR: ") % result['error'])
                return
            
            if len(result['songlist']) == 0:
                    self.output.InsertText(0, _("No result for %s - %s\r") % (artist, song))
                    return
                
            if len(result['songlist'].values()) == 1:
                songSelected = result['songlist'][0]
            else:
                choices = []
                
                for results in result['songlist'].values():
                    choices.append("%s - %s"  % (results[1], results[0]))
                    
                choiceDialog = ChoiceDialog(self, choices = choices,
                                                    prompt = _("Make your choice"),
                                                    title = _("Results"),
                                                    size = (300, 200))
                if choiceDialog.ShowModal() == 'ok':
                    songSelected = result['songlist'][choiceDialog.choice]
                
                choiceDialog.Destroy()
                        
            if len(songSelected) != 3:
                self.output.InsertText(0, _("No result for %s - %s\r") % (artist, song))
                return
            
             # Download lyrics
            lyrics['artist'] = songSelected[0]
            lyrics['song'] = songSelected[1]
            lyrics['hid'] = songSelected[2]
            lyrics['lyrics'] = search.ShowLyrics(lyrics['hid'])
                     
            # Detect errors
            if lyrics['lyrics'].has_key('error'):
                self.output.InsertText(0, _("ERROR: ") % lyrics['lyrics']['error'])
                self.output.InsertText(0, _("Lyrics found but NOT added for %s - %s") % (artist, song))
                return
                
            try:
                audio.add(USLT(encoding=3, desc='', lang='eng', text=lyrics['lyrics']['lyrics']))
                audio.save()
            
            except Exception,err:
                self.output.InsertText(0, _("Lyrics found but NOT added for %s - %s") % (artist, song))
                return
            
            self.output.InsertText(0, _("Lyrics found and added for %s - %s\r") % (artist, song))
            added += 1
            self.statusBar[2] = _("Tags added: %s") % added
            lyrics['lyrics']['lyrics'] = None

            if not cancel:
                break
            
        dlg.Destroy()
        
    def Browse(self, event=None):
        dirDialog = DirectoryDialog(self)
        try:
            if dirDialog.ShowModal() == 'ok':
                dirname = dirDialog.GetPath()
                self.musicPath.SetValue(dirname)
        finally:
            dirDialog.Destroy()
            
    def Analyze(self, musicPath):
        """ Scan given directory.
        
        Return ({id: [file, status]}, number of files, incomplete files)"""
        
        fileList = {}       # Dict: {id: [file, status]}
        id = 0              # File ID
        missed = 0          # Number of missed tags
        self.statusBar[0] = _("Number of files: %s") % 0
        self.statusBar[1] = _("Missed tags: %d") % 0
        
        # Looking for audio files
        for root, dirs, files in os.walk(musicPath):
            for file in files:
                if file[-3:] == 'mp3':
                    self.statusBar[0] = _("Number of files: %s") % str(id+1)
                    status = None
                    fullpath = os.path.realpath(os.path.join(root, file))
                    
                    try:
                        audio = MP3(fullpath)
                        
                    except Exception, err:
                        self.output.InsertText(0, _("Error (while scanning (%s): %s\r") % (file, err))
                        return
                    
                    for items in audio:
                        if items[:4] == 'USLT':
                            if len(str(ID3(fullpath).getall(items)[0])) >= 100:
                                status = items
                                
                    if status is None:
                        missed += 1
                        self.statusBar[1] = _("Missed tags: %d") % missed
                        
                    fileList[id] = [fullpath, status]
                    id += 1
        
        return (fileList, id, missed)

class PreferencesDialog(CustomDialog):
    """ Create Preferences window. """
    
    def Body(self):
        # Main Panel
        mainPanel = VerticalPanel(self)
        
        # Options
        gPanel = FlexGridPanel(mainPanel, rows = 3, cols = 3, hgap = 5, vgap = 5)
        
        self.baseDir = TextBox(gPanel, Value=os.path.expanduser(config.get('Output', 'BaseDir')))
        self.fileModel = TextBox(gPanel, Value=config.get('Output', 'Model'))
        self.fileModel.OnChar = self._RegenerateExample
        self.fileExample = Label(gPanel, GenerateFilename(artist = 'Simple Plan', song = 'Thank You', album = 'Still Not Getting Any'))
        
        gPanel.AddComponent(0, 0, Label(gPanel, _("Output directory"), align='right'), border=5)
        gPanel.AddComponent(0, 1, Label(gPanel, _("File model"), align='right'), border=5)
        gPanel.AddComponent(0, 2, Label(gPanel, _("Example"), align='right'), border=5)
        gPanel.AddComponent(1, 0, self.baseDir)
        gPanel.AddComponent(1, 1, self.fileModel)
        gPanel.AddComponent(1, 2, self.fileExample, border=6)
        gPanel.AddComponent(2, 0, Button(gPanel, _("Browse"), self.OnBrowse))
        gPanel.Pack()
        
        gPanel.AddGrowableCol(1)
        
        # Buttons
        vPanel = HorizontalPanel(mainPanel)
        vPanel.AddComponent(Button(self.vPanel, _("Ok"), event=self.OnOk), border=3, align='center')
        vPanel.AddComponent(Button(self.vPanel, _("Abort"), event=self.OnQuit), border=3, align='center')
        vPanel.Pack()
     
        mainPanel.AddComponent(Label(mainPanel, _("Global preferences")), border=8, align='center')
        mainPanel.AddComponent(gPanel, border=10)
        mainPanel.AddComponent(self.vPanel, border=10, align='center')
        mainPanel.Pack()
        
        self.AddComponent(mainPanel, expand = 'both', border=10)
        self.Pack()
        
    def OnQuit(self, event=None):
        self.Close()
    
    def OnOk(self, event=None):
        """ Save and close. """
        config.set('Output', 'basedir', self.baseDir.GetValue())
        config.set('Output', 'model', self.fileModel.GetValue())
        config.write(open('lyricistCow.cfg','w'))
        self.Close()
        
    def OnBrowse(self, event=None):
        dirDialog = DirectoryDialog(self)
        try:
            if dirDialog.ShowModal() == 'ok':
                dirname = dirDialog.GetPath()
                self.baseDir.SetValue(dirname)
        finally:
            dirDialog.Destroy()
    
    def _RegenerateExample(self, event=None):
        self.fileExample.SetLabel(GenerateFilename(model = self.fileModel.GetValue(),
                                  artist = 'Simple Plan', song = 'Thank You',
                                  album = 'Still Not Getting Any'))
        event.Skip()
        
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
        infoTab.infoText += "\nPython: %s\nwxPython: %s" % (platform.python_version(),
                                                            wx.VERSION_STRING)
        
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
        
if __name__ == "__main__":
    
    # Log error
    errorFile = open('error.log', 'w')
    sys.stderr = errorFile
    
    # Configuration file
    try:
        configFile = os.path.join(os.path.abspath('musicalcow.cfg'))
        config = ConfigParser.ConfigParser()
        config.readfp(open(configFile, 'r'))
    except Exception, err:
        configFile = open(os.path.join(os.path.abspath('musicalcow.cfg')), 'w')
        configFile.write("""
[Output]
basedir = ~/lyrics/
model = %artist/%album/%artist - %song.txt

[MusicRoot]
directory = ~/
""")
        configFile.close()
        configFile = os.path.join(os.path.abspath('musicalcow.cfg'))
        config = ConfigParser.ConfigParser()
        config.readfp(open(configFile, 'r'))
        
    # Gettext init
    gettext.bindtextdomain('musicalcow')
    locale.setlocale(locale.LC_ALL, '')
    gettext.textdomain('musicalcow')
    gettext.install('musicalcow', os.path.abspath('locales'), unicode=1)
    
    # Creates windows
    lyricsCow = Application(MainFrame, title="lyricistCow")
    lyricsCow.Run()