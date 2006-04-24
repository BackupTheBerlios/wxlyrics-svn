from distutils.core import setup
import py2exe
import sys

# If run without args, build executables, in quiet mode.
if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = "0.1.4.24"
        self.company_name = "ZeVlad"
        self.copyright = "2006 - Vladimir Svoboda"
        self.name = "wxLyrics"

################################################################
# A program using wxPython

# The manifest will be inserted as resource into wxlyrics.exe.  This
# gives the controls the Windows XP appearance (if run on XP ;-)
#
# Another option would be to store it in a file named
# wxlyrics.exe.manifest, and copy it with the data_files option into
# the dist-dir.
#
manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24

wxlyrics = Target(
    # used for the versioninfo resource
    description = "A simple lyrics viewer",

    # what to build
    script = "wxlyrics.pyw",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog = "wxlyrics"))],
##    icon_resources = [(1, "icon.ico")],
    dest_base = "wxlyrics")

################################################################

setup(
    url = "https://developer.berlios.de/projects/wxlyrics/",
    description = "Download and display lyrics",
    license = "GNU GPL v2",
    options = {"py2exe": {
                        "compressed": 1,
                        "optimize": 2,
                        "bundle_files": 1,
                        "packages": ["encodings"],
                        "dist_dir": "C:\wxLyrics"}},
    zipfile = None,
    data_files=[(".",["COPYING" , "AUTHORS", "TODO", "wxlyrics.cfg"])],
    windows = [wxlyrics])
