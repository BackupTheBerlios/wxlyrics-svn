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

import os
import ConfigParser

from wax import *

configFile = os.path.join(os.path.abspath('musicalcow.cfg'))
config = ConfigParser.ConfigParser()
config.readfp(open(configFile, 'r'))

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

class PreferencesDialog(CustomDialog):
    """ Create Preferences window. """
    
    def Body(self):
        
        # lyricsCow options
        lyricsCow = GroupBox(self, text=_("lyricsCow options"), direction='v')
        gPanel = FlexGridPanel(lyricsCow, rows=3, cols=3, hgap=5, vgap=5)
        
        self.baseDir = TextBox(gPanel,
             Value=os.path.expanduser(config.get('Output', 'BaseDir')))
        self.fileModel = TextBox(gPanel, Value=config.get('Output', 'Model'))
        self.fileModel.OnChar = self._RegenerateExample
        self.fileExample = Label(gPanel, GenerateFilename(
                                         artist='Simple Plan',
                                         song='Thank You',
                                         album='Still Not Getting Any'))
        
        gPanel.AddComponent(0, 0, Label(gPanel, _("Output directory"),
                            align='right'), border=5)
        gPanel.AddComponent(0, 1, Label(gPanel, _("File model"),
                            align='right'), border=5)
        gPanel.AddComponent(0, 2, Label(gPanel, _("Example"), align='right'),
                            border=5)
        gPanel.AddComponent(1, 0, self.baseDir)
        gPanel.AddComponent(1, 1, self.fileModel)
        gPanel.AddComponent(1, 2, self.fileExample, border=6)
        gPanel.AddComponent(2, 0, Button(gPanel, _("Browse"), self.OnBrowse))
        gPanel.AddGrowableCol(1)
        gPanel.Pack()
        
        lyricsCow.AddComponent(gPanel)
        lyricsCow.Pack()
        
        # podCow options
        podCow = GroupBox(self, text=_("podCow options"), direction='v')
        gPanel = FlexGridPanel(podCow, rows=1, cols=3, hgap=5, vgap=5)
        
        self.musicRoot = TextBox(gPanel,
             Value=os.path.expanduser(config.get('MusicRoot', 'Directory')))
        
        gPanel.AddComponent(0, 0, Label(gPanel, _("Library root:"),
                            align='right'), border=5)
        gPanel.AddComponent(1, 0, self.musicRoot, expand='h')
        gPanel.AddComponent(2, 0, Button(gPanel, _("Browse"), self.OnBrowse))
        gPanel.AddGrowableCol(1)
        gPanel.Pack()
        
        podCow.AddComponent(gPanel)
        podCow.Pack()
        
        # Buttons
        butPnl = HorizontalPanel(self)
        butPnl.AddComponent(Button(butPnl, _("Ok"), event=self.OnOk),
                            border=3, align='center')
        butPnl.AddComponent(Button(butPnl, _("Abort"), event=self.OnQuit),
                            border=3, align='center')
        butPnl.Pack()
        
        self.AddComponent(lyricsCow, border=10)
        self.AddComponent(podCow, border=10, expand='h')
        self.AddComponent(butPnl, border=10, align='center')
        
        self.Pack()
        
    def OnQuit(self, event=None):
        self.Close()
    
    def OnOk(self, event=None):
        """ Save and close. """
        
        config.set('Output', 'basedir', self.baseDir.GetValue())
        config.set('Output', 'model', self.fileModel.GetValue())
        config.set('MusicRoot', 'directory', self.musicRoot.GetValue())
        config.write(open('musicalcow.cfg','w'))
        self.Close()
        
    def OnBrowse(self, event=None, mode='lyricscow'):
        dirDialog = DirectoryDialog(self)
        try:
            if dirDialog.ShowModal() == 'ok':
                dirname = dirDialog.GetPath()
                if mode == 'lyricsCow':
                    self.baseDir.SetValue(dirname)
                else:
                    self.musicRoot.SetValue(dirname)
        finally:
            dirDialog.Destroy()
    
    def _RegenerateExample(self, event=None):
        self.fileExample.SetLabel(GenerateFilename(
                                  model=self.fileModel.GetValue(),
                                  artist='Simple Plan',
                                  song='Thank You',
                                  album='Still Not Getting Any'))
        event.Skip()