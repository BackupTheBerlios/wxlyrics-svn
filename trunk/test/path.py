import os
import os.path

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT

# Results from different os.path function
lyricsPath = "~/lyrics/Manau/On Peut Tous Rever/Manau - Con J'pense.txt"
print os.path.split(os.path.expanduser(lyricsPath))
print os.path.dirname(lyricsPath)
print os.path.basename(lyricsPath)

# Walk into music directory
musicPath = os.path.expanduser("G:\Documents\Ma musique")
fileNum = 0
fileList = {}

for root, dirs, files in os.walk(musicPath):
    for file in files:
        if file[-3:] == 'mp3':
            i = 0
            status = None
            file = os.path.realpath(os.path.join(root, file))
            
            try:
                audio = MP3(file)
                
                for items in audio:
                    if items[:4] == 'USLT' and i <= 1:
                        status = items
                        i += 1
                        
            except Exception, err:
                print err
                
            fileList[fileNum] = [file, status]
            fileNum += 1

for file, status in fileList.values():
    if status is not None:
        print file
