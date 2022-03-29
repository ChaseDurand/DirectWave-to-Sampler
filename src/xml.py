import gzip
import os
import pathlib
import shutil
import xml.etree.ElementTree as ET

# Given a sample table, create sampler instrument.
# Build xml sampler, copy to User Library.
# Copy samples to User Library.
def createSampler(samplerName, table, userLibrary):
    # Prepare empty sampler preset.
    template = ET.parse("src/samplerTemplate.xml")
    insertionLocation = template.getroot().find('MultiSampler')\
        .find('Player').find('MultiSampleMap').find('SampleParts')
    insertionLocation.text = "\n                    "

    sampleDirectory = createSampleDir(samplerName, userLibrary)
    tableSize = len(table)
    # For every sample, add to xml and copy to User Library.
    for i in range(0, tableSize):
        # Need to format last entry differently.
        if i == tableSize-1:
            isLast = True
        else:
            isLast = False
        insertSampleInXML(table[i], insertionLocation, i, isLast, samplerName)
        shutil.copy(str(table[i].fullPath), str(sampleDirectory)) # Copy sample to User Library

    # TODO change this to write xml to tmp directory.
    # Save xml as adv in User Library instrument presets.
    instrumentDst = str(pathlib.Path(userLibrary, "Presets", "Instruments", "Sampler", samplerName+".adv"))
    template.write("output.xml", encoding="UTF-8", xml_declaration=True, short_empty_elements=False)
    with open("output.xml", "rb") as f_in:
        with gzip.open(instrumentDst, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    return

# Create directory for audio samples in User Library.
# If directory already exists, print error and quit.
def createSampleDir(samplerName, destLocation):
    sampleDirectory = pathlib.Path(destLocation, "Samples", "Imported", samplerName)
    if sampleDirectory.exists():
        print("Error: destination directory already exists!")
        print(sampleDirectory)
        exit(1)
    else:
        print("Created sample directory: ", sampleDirectory)
        sampleDirectory.mkdir(parents=True, exist_ok=True)
    return sampleDirectory

# Given a sample, add to XML
def insertSampleInXML(sample, insertionLocation, index, isLast, samplerName):
    newElement = ET.parse("src/multiSampleTemplate.xml").getroot()
    # Add ID
    newElement.set("Id", str(index))
    # Add name
    newElement.find("Name").set("Value", sample.fileName[:-4])
    # Add filename
    newElement.find("SampleRef").find("FileRef").find("Name").set("Value", str(sample.fileName))
    newElement.find("SampleRef").find("SourceContext").find("SourceContext")\
        .find("OriginalFileRef").find("FileRef").find("Name")\
        .set("Value", str(sample.fileName))
    # Add keyrange
    newElement.find("KeyRange").find("Min").set("Value", str(sample.keyRangeMin))
    newElement.find("KeyRange").find("Max").set("Value", str(sample.keyRangeMax))
    newElement.find("KeyRange").find("CrossfadeMin").set("Value", str(sample.keyRangeMin))
    newElement.find("KeyRange").find("CrossfadeMax").set("Value", str(sample.keyRangeMax))
    # Add velocity range
    # TODO
    # Add root key
    newElement.find("RootKey").set("Value", str(sample.rootNote))
    # Add sample end
    newElement.find("SampleEnd").set("Value", str(sample.sampleEnd))
    newElement.find("SustainLoop").find("End").set("Value", str(sample.sampleEnd))
    newElement.find("ReleaseLoop").find("End").set("Value", str(sample.sampleEnd))
    # Add path
    newElement.find("SampleRef").find("FileRef").find("RelativePath")\
        .findall("RelativePathElement")[-1].set("Dir", str(samplerName))
    newElement.find("SampleRef").find("FileRef").find("SearchHint")\
        .find("PathHint").findall("RelativePathElement")[-1].set("Dir", str(samplerName))
    # Create and add browser content path
    bcPath = createBrowserContentPath(sample.fileName, samplerName)
    newElement.find("SampleRef").find("SourceContext").find("SourceContext")\
        .find("BrowserContentPath")\
        .set("Value", bcPath)
    # Add filesize
    newElement.find("SampleRef").find("FileRef").find("SearchHint")\
        .find("FileSize").set("Value", str(os.path.getsize(str(sample.fullPath))))
    # Add last modification date (unix epoch time)
    lastModTime = round(os.path.getmtime(str(sample.fullPath)))
    newElement.find("SampleRef").find("LastModDate").set("Value", str(lastModTime))
    # Add defaultduration
    newElement.find("SampleRef").find("DefaultDuration").set("Value", str(sample.sampleEnd+1))
    # Add defaultSamplerate
    # TODO

    # Need to format differently if last sample.
    if isLast:
        newElement.tail = "\n                "
    else:
        newElement.tail = "\n                    "
    insertionLocation.append(newElement)
    return

def createBrowserContentPath(sampleName, samplerName):
    return "query:UserLibrary#Samples:Imported:"+samplerName+":"\
        +sampleName.replace("#","%23")