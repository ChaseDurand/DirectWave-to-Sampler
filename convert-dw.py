#!/usr/bin/env python3

from dataclasses import dataclass
from math import ceil
import pathlib
import sys
import wave
from src.midi import getNoteFromStr
from src.library import getLibraryLocation
from src.xml import createSampler

@dataclass
class Sample:
    fullPath: pathlib.PosixPath
    fileName: pathlib.PosixPath
    rootNote: int
    keyRangeMin: int
    keyRangeMax: int
    velocityRoot: int
    # velocityMin: int
    # velocityMax: int
    # zoneMin: int
    # zoneMax: int
    sampleEnd: int
    # Use root note to compare samples
    def __lt__(self, other):
        return self.rootNote < other.rootNote

def main():
    #Confirm only arguments are script+directory
    if(len(sys.argv) != 2):
        print("Erorr: Expected 1 argument but found",len(sys.argv)-1)
        if(len(sys.argv) == 1):
            print("Error: Please provide wav folder path as argument!")
        exit(1)

    # Get OS
    if sys.platform == "darwin":
        IS_MAC = True
    else:
        IS_MAC = False

    wavDirectory = pathlib.Path(sys.argv[1])
    if(wavDirectory.is_dir() == False):
        print("Error: path is not a directory!")
        exit(1)
    samplerName = wavDirectory.name

    sampleTable = []
    for wav in wavDirectory.glob("*.wav"):
        rootNoteVelocity = wav.stem[len(samplerName):]
        # Confirm file name is samplerName_rootNote_velocity
        if(len(rootNoteVelocity.split("_")) != 3):
            print("Error! Unable to parse wav filename:", wav.stem)
            exit(1)
        # exit()
        rootNoteStr = rootNoteVelocity.split("_")[1]
        velocityStr = rootNoteVelocity.split("_")[2]
        frameEnd = wave.open(str(wav), 'rb').getnframes() -1
        sampleTable.append(Sample(wav,
                                  wav.name,
                                  getNoteFromStr(rootNoteStr),
                                  0,
                                  0,
                                  velocityStr,
                                  frameEnd))
    
    # Sort table (by rootNote)
    # TODO sort and parse by velocity
    # TODO change to find key zones vs calulating each time
    sampleTable.sort()
    tableSize = len(sampleTable)
    # if(tableSize >= 2):
    for i in range(0,tableSize):
        if (i == 0):
            sampleTable[i].keyRangeMin = 0
        else:
            lowerRangeDelta = sampleTable[i].rootNote - sampleTable[i-1].rootNote
            sampleTable[i].keyRangeMin = sampleTable[i].rootNote-ceil(lowerRangeDelta/2)+1

        if (i == tableSize-1):
                sampleTable[i].keyRangeMax = 127
        else:
            upperRangeDelta = sampleTable[i+1].rootNote - sampleTable[i].rootNote
            sampleTable[i].keyRangeMax = sampleTable[i].rootNote+round(upperRangeDelta/2)

    print("Found", len(sampleTable), ".wav files.")

    # Get User Library location
    userLibrary = getLibraryLocation(IS_MAC)
    print("Found User Library:", str(userLibrary))

    print("Creating sampler: ", samplerName)
    createSampler(samplerName, sampleTable, userLibrary)
    print("Complete.")
    exit(0)

if __name__ == '__main__':
    main()