import os
import os.path

# Results from different os.path function
lyricsPath = "~/lyrics/Manau/On Peut Tous Rever/Manau - Con J'pense.txt"
print os.path.split(os.path.expanduser(lyricsPath))
print os.path.dirname(lyricsPath)
print os.path.basename(lyricsPath)

# Walk into music directory

musicPath = os.path.expanduser("~/Documents/Ma musique/")
for root, dirnames, filenames in os.walk(musicPath):
	print root
	for dirs in dirnames:
		print dirs
