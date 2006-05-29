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

from wax import *

class PreferencesDialog(CustomDialog):
    """ Create Preferences window. """
    
    def Body(self):
        # Main Panel
        mainPanel = VerticalPanel(self)
        
        # Options
        gPanel = FlexGridPanel(mainPanel, rows=3, cols=3, hgap=5, vgap=5)
        
        self.baseDir = TextBox(gPanel, Value=os.path.expanduser(config.get('Output', 'BaseDir')))
        self.fileModel = TextBox(gPanel, Value=config.get('Output', 'Model'))
        self.fileModel.OnChar = self._RegenerateExample
        self.fileExample = Label(gPanel, GenerateFilename(artist='Simple Plan',
                           song='Thank You', album='Still Not Getting Any'))
        
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
        butPnl = HorizontalPanel(mainPanel)
        butPnl.AddComponent(Button(butPnl, _("Ok"), event=self.OnOk),
                            border=3, align='center')
        butPnl.AddComponent(Button(butPnl, _("Abort"), event=self.OnQuit),
                            border=3, align='center')
        butPnl.Pack()
     
        mainPanel.AddComponent(Label(mainPanel, _("Global preferences")),
                               border=8, align='center')
        mainPanel.AddComponent(gPanel, border=10)
        mainPanel.AddComponent(butPnl, border=10, align='center')
        mainPanel.Pack()
        
        self.AddComponent(mainPanel, expand = 'both', border=10)
        self.Pack()
        
    def OnQuit(self, event=None):
        self.Close()
    
    def OnOk(self, event=None):
        """ Save and close. """
        
        config.set('Output', 'basedir', self.baseDir.GetValue())
        config.set('Output', 'model', self.fileModel.GetValue())
        config.write(open('musicalcow.cfg','w'))
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
        self.fileExample.SetLabel(GenerateFilename(
                                  model=self.fileModel.GetValue(),
                                  artist='Simple Plan',
                                  song='Thank You',
                                  album='Still Not Getting Any'))
        event.Skip()        