#
#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
#

# podCow
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
import os
import locale
import gettext
import ConfigParser
import time

from wax import *
from wax.tools.choicedialog import ChoiceDialog
from wax.tools.progressdialog import ProgressDialog
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT

from searchlyrics import SearchLyrics

class MainFrame(Frame):
    """ Main window with menu, status bar and notebook (tabs) for lyrics. """
    
    def Body(self):
        error = None
        self.result = [None]
        self.filename = [None]
        
        # Create status bar
        self.statusBar = StatusBar(self, numpanels=3)
        self.SetStatusBar(self.statusBar)
        
        # Create menu and body
        self.CreateMenu()
        self.CreateBody()
        self.SetIcon('wxlyrics.ico')
        
    def CreateBody(self):
        """ Contenu de la frame """
        
        # Main Panel
        mainPanel = VerticalPanel(self)
        
        gPanel = HorizontalPanel(mainPanel)
        
        self.musicPath = TextBox(gPanel, Value=config.get('MusicRoot', 'directory'))
        
        gPanel.AddComponent(Label(gPanel, _("Music Directory:"), align='right'), border=8)
        gPanel.AddComponent(self.musicPath, expand='h', border=5)
        gPanel.AddComponent(Button(gPanel, _("Browse"), self.OnBrowse), border=5)
        gPanel.Pack()
        
        buttonPanel = HorizontalPanel(mainPanel)
        self.scan = Button(buttonPanel, _("Scan"), event=self.OnAnalyze)
        self.add = Button(buttonPanel, _("Add lyrics"), event=self.OnAddLyrics)
        buttonPanel.AddComponent(self.scan, border=5, align='center')
        buttonPanel.AddComponent(self.add, border=5, align='center')
        buttonPanel.Pack()
        
        mainPanel.AddComponent(gPanel, expand='h', border=5)
        mainPanel.AddComponent(buttonPanel, border=5, align='center')
        self.output = TextBox(mainPanel, multiline=1)
        mainPanel.AddComponent(self.output, expand='both')
        mainPanel.Pack()
        
        self.AddComponent(mainPanel, expand='both')
        
        # Window Settings
        self.Pack()
        self.SetSize((400, 170))
    
    def CreateMenu(self):
        """ Create menu bar """
        menuBar = MenuBar(self)
        
        fileMenu = Menu(self)
        fileMenu.Append(_("E&xit"), self.OnQuit, hotkey = "Ctrl-Q")
        
        helpMenu = Menu(self)
        helpMenu.Append(_("&Help"), self.OnHelp, hotkey = "F1")
        helpMenu.AppendSeparator()
        helpMenu.Append(_("&About podCow"), self.OnAbout)
        
        menuBar.Append(fileMenu, _("&File"))
        menuBar.Append(helpMenu, "&?")
        
    def OnQuit(self, event=None):
        """ Quit application """
        quitDialog = MessageDialog(self, text = _("Do you really want to quit wxLyrics"),
                                       icon = "question", yes_no = 1)
        if quitDialog.ShowModal() == 'yes':
            self.Close(True)
    
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
        
    def OnAbout(self, event=None):
        """ About dialog. """
        
        aboutDialog = AboutDialog(self, _("About podCow"))
        aboutDialog.ShowModal()
        aboutDialog.Destroy()
    
    def OnHelp(self, event=None):
        """ Help dialog. """
        
        helpMessage = _("Fill the fields 'artist' and 'song title'."
                        "You will receive a list of song")
        helpFrame = MessageDialog(self, _("Help"), helpMessage, ok = 1,
                                      icon = "information")
        helpFrame.ShowModal()
        helpFrame.Destroy()
        
    def OnBrowse(self, event=None):
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
                    file = os.path.realpath(os.path.join(root, file))
                    
                    try:
                        audio = MP3(file)
                        
                    except Exception, err:
                        self.output.InsertText(0, _("Error (while scanning (%s - %s): %s\r") % (artist, song, err))
                        return
                    
                    for items in audio:
                        if items[:4] == 'USLT':
                            if len(str(ID3(file).getall(items)[0])) >= 100:
                                status = items
                                
                    if status is None:
                        missed += 1
                        self.statusBar[1] = _("Missed tags: %d") % missed
                        
                    fileList[id] = [file, status]
                    id += 1
        
        return (fileList, id, missed)

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
    podCow = Application(MainFrame, title="The Pod Cow")
    podCow.Run()