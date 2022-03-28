from dbm.ndbm import library
import xml.etree.ElementTree as ET
import os
import gzip
import shutil
import pathlib
from packaging import version


def createSampleDir(samplerName, destLocation):
    # If directory exists, print error and quit
    # If not, create directory for samples
    sampleDirectory = pathlib.Path(destLocation, "Samples", "Imported", samplerName)
    print(sampleDirectory)
    if sampleDirectory.exists():
        print("Error: destination directory already exists!")
        exit(1)
    else:
        sampleDirectory.mkdir(parents=True, exist_ok=True)
    return sampleDirectory


# Given a sample table, create sampler instrument
# Create xml
# For every sample, add to xml
# Zip xml as instrument
# Copy to destination
def createSampler(samplerName, table, userLibrary):
    template = ET.parse("templates/samplerTemplate.xml")
    templateRoot = template.getroot()
    insertionLocation = templateRoot.find('MultiSampler')
    insertionLocation = insertionLocation.find('Player')
    insertionLocation = insertionLocation.find('MultiSampleMap')
    insertionLocation = insertionLocation.find('SampleParts')
    insertionLocation.text = "\n                    "

    sampleDirectory = createSampleDir(samplerName, userLibrary)
    instrumentDst = str(pathlib.Path(userLibrary, "Presets", "Instruments", "Sampler", samplerName+".adv"))

    tableSize = len(table)
    for i in range(0, tableSize):
        if i == tableSize-1:
            isLast = True
        else:
            isLast = False
        insertSampleInXML(table[i], insertionLocation, i, isLast, samplerName)
        copySample(table[i], sampleDirectory)

    # TODO change this to write to tmp directory
    template.write("output.xml", encoding="UTF-8", xml_declaration=True, short_empty_elements=False)

    with open("output.xml", "rb") as f_in:
        with gzip.open(instrumentDst, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    return


def getLibraryLocation():
    macLocationPart = "/Library/Preferences/Ableton"
    paths = pathlib.Path(os.path.expanduser("~") + macLocationPart)

    directories = paths.glob("Live*")
    maxVersion = version.parse("0.0")
    for dir in directories:
        maxVersion = max(maxVersion, version.parse(dir.name[5:]))

    dirTail = "Live " + str(maxVersion)
    libCfg = "Library.cfg"
    libraryPath = pathlib.Path(str(paths), dirTail, libCfg)

    libraryCfg = ET.parse(libraryPath)
    libraryCfgRoot = libraryCfg.getroot()

    return pathlib.Path(libraryCfgRoot.find("ContentLibrary").find("UserLibrary")\
      .find("LibraryProject").find("DisplayName").get("Value"))






        # fullPath
        # fileName: pathlib.PosixPath
        # rootNote: int
        # velocity: int
        # keyRangeMin: int
        # keyRangeMax: int
        # sampleEnd: int

# Given a sample, add to XML
def insertSampleInXML(sample, insertionLocation, index, isLast, samplerName):
    newElement = ET.parse("templates/multiSampleTemplate.xml").getroot()

    # Add ID
    newElement.set("Id", str(index))
    # Add name
    newElement.find("Name").set("Value", sample.fileName[:-4])
    # Add keyrange
    newElement.find("KeyRange").find("Min").set("Value", str(sample.keyRangeMin))
    newElement.find("KeyRange").find("Max").set("Value", str(sample.keyRangeMax))
    newElement.find("KeyRange").find("CrossfadeMin").set("Value", str(sample.keyRangeMin))
    newElement.find("KeyRange").find("CrossfadeMax").set("Value", str(sample.keyRangeMax))
    # Add velocity range
    # Add root key
    newElement.find("RootKey").set("Value", str(sample.rootNote))
    # Add sample end
    newElement.find("SampleEnd").set("Value", str(sample.sampleEnd))

    newElement.find("SustainLoop").find("End").set("Value", str(sample.sampleEnd))
    newElement.find("ReleaseLoop").find("End").set("Value", str(sample.sampleEnd))

    # Add path

    newElement.find("SampleRef").find("FileRef").find("RelativePath")\
        .findall("RelativePathElement")[-1].set("Dir", str(samplerName))

    newElement.find("SampleRef").find("FileRef").find("Name").set("Value", str(sample.fileName))

    newElement.find("SampleRef").find("FileRef").find("SearchHint")\
        .find("PathHint").findall("RelativePathElement")[-1].set("Dir", str(samplerName))

    newElement.find("SampleRef").find("FileRef").find("SearchHint")\
        .find("FileSize").set("Value", str(os.path.getsize(str(sample.fullPath))))

    newElement.find("SampleRef").find("SourceContext").find("SourceContext")\
        .find("OriginalFileRef")\
        .find("FileRef").find("Name").set("Value", str(sample.fileName))


    # Create and add browser content path
    bcPath = createBrowserContentPath(sample.fileName, samplerName)
    newElement.find("SampleRef").find("SourceContext").find("SourceContext")\
        .find("BrowserContentPath")\
        .set("Value", bcPath)

    # Add filesize

    # Add LastModDate (unix epoch time)
    lastModTime = round(os.path.getmtime(str(sample.fullPath)))
    newElement.find("SampleRef").find("LastModDate").set("Value", str(lastModTime))

    # Add SourceContext


    # Add defaultduration
    newElement.find("SampleRef").find("DefaultDuration").set("Value", str(sample.sampleEnd+1))

    # Add defaultSamplerate

    # <DefaultSampleRate Value=""></DefaultSampleRate>

    if isLast:
        newElement.tail = "\n                "
    else:
        newElement.tail = "\n                    "
    insertionLocation.append(newElement)
    return

# Copy file to destination directory
def copySample(sample, sampleDir):
    shutil.copy(str(sample.fullPath), str(sampleDir))
    return


def createBrowserContentPath(sampleName, samplerName):
    return "query:UserLibrary#Samples:Imported:"+samplerName+":"\
        +sampleName.replace("#","%23")
