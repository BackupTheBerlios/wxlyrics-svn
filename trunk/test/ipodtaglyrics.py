print "Mutagen"

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT

#file = "/mnt/data/Documents/Ma musique/The Rasmus/Hide From The Sun/10 - Heart Of Misery.mp3"
#file = "G:\Documents\Ma musique\Simple Plan\No Pads, No Helmets ... Just Balls\\01 - I'd Do Anything.mp3"
#file = "G:\Documents\Ma musique\Avril Lavigne\Let Go\\06 - Unwanted.mp3"
file = "G:\Documents\Ma musique\Sum 41\Go Chuck Yourself\\06 - We're All To Blame.mp3"
#file = "/mnt/data/Documents/Ma musique/Sum 41/Go Chuck Yourself/20 - Fat Lip.mp3"
audio = MP3(file)

i = 0
match = None
for items in audio:
    print items
    if items[:4] == "USLT" and i <= 1:
        match = items
        i += 1

print "---"

audio = ID3(file)

if match is not None:
    print match
    print audio.getall(match)[0]
else:
    print "No lyrics"
    lyrics = 'wazaa'
    #audio.add(USLT(encoding=3,desc='', lang=u'eng', text=lyrics))
    #audio.save()
    
print "-----------"

print "Tagger"

from tagger import *

audio = ID3v2(file)

i = 0
match = None
for frame in audio.frames:
    print "%s (%s) %s" % (frame.fid, frame.encoding, str(frame.strings))
    
    if frame.fid[:4] == "USLT" and i <= 1:
        match = frame
        i += 1
        
print match.strings