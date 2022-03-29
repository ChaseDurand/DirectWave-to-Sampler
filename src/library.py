import os
from packaging import version
import pathlib
import xml.etree.ElementTree as ET

# Get the Live User Library location from Library.cfg.
def getLibraryLocation(IS_MAC):
    # Library.cfg location is platform dependent.
    if IS_MAC:
        # Get preference folders
        macLocationPart = "/Library/Preferences/Ableton"
        paths = pathlib.Path(os.path.expanduser("~") + macLocationPart)
        # Find most recent version
        directories = paths.glob("Live*")
        maxVersion = version.parse("0.0")
        for dir in directories:
            maxVersion = max(maxVersion, version.parse(dir.name[5:]))
        # Parse Library.cfg as .xml
        dirTail = "Live " + str(maxVersion)
        libCfg = "Library.cfg"
        libraryPath = pathlib.Path(str(paths), dirTail, libCfg)
        libraryCfg = ET.parse(libraryPath)
        libraryCfgRoot = libraryCfg.getroot()
        # Return User Library path
        return pathlib.Path(libraryCfgRoot.find("ContentLibrary").find("UserLibrary")\
        .find("LibraryProject").find("DisplayName").get("Value"))
    else:
        # TODO implement for Windows
        # Windows: Users\[username]\AppData\Roaming\Ableton\Live x.x.x\Preferences\
        print("Error: Only OSX is currently supported.")
        exit(1)