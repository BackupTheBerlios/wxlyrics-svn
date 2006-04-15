import os.path

path = "~/lyrics/Manau/On Peut Tous Rever/Manau - Con J'pense.txt"
print os.path.split(os.path.expanduser(path))
print os.path.dirname(path)
print os.path.basename(path)