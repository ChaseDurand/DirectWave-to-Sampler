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
    velocityMin: int
    velocityMax: int
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
        rootNoteStr = rootNoteVelocity.split("_")[1]
        velocityStr = int(rootNoteVelocity.split("_")[2])
        frameEnd = wave.open(str(wav), 'rb').getnframes() -1
        sampleTable.append(Sample(wav,
                                  wav.name,
                                  getNoteFromStr(rootNoteStr),
                                  0,
                                  0,
                                  velocityStr,
                                  0,
                                  0,
                                  frameEnd))

    # Determine number of velocity layers per note
    velocityCount = {}

    for sample in sampleTable:
        if sample.rootNote in velocityCount:
            velocityCount[sample.rootNote] += 1
        else:
            velocityCount[sample.rootNote] = 1

    velocityCycles = next(iter(velocityCount.values()))

    if not all(val == velocityCycles for val in velocityCount.values()):
        print("Error: missing samples for velocity cycles!")
        exit(1)

    # Sort by root note then velocity
    sampleTable = sorted(sampleTable, key = lambda x: (x.rootNote, x.velocityRoot))

    i = 0
    tableSize = len(sampleTable)
    while(i != tableSize):
        j = 0
        while(j < velocityCycles):
            # Handle velocity ranges
            if (j == 0):
                sampleTable[i+j].velocityMin = 0
            else:
                lowerRangeDelta = sampleTable[i+j].velocityRoot - sampleTable[i+j-1].velocityRoot
                sampleTable[i+j].velocityMin = sampleTable[i+j].velocityRoot-ceil(lowerRangeDelta/2)+1

            if (j == velocityCycles-1):
                sampleTable[i+j].velocityMax = 127
            else:
                upperRangeDelta = sampleTable[i+j+1].velocityRoot - sampleTable[i+j].velocityRoot
                sampleTable[i+j].velocityMax = sampleTable[i+j].velocityRoot+round(upperRangeDelta/2)
            

            # Handle note ranges
            if (i == 0):
                sampleTable[i+j].keyRangeMin = 0
            else:
                lowerRangeDelta = sampleTable[i+j].rootNote - sampleTable[(i+j)-velocityCycles].rootNote
                sampleTable[i+j].keyRangeMin = sampleTable[i+j].rootNote-ceil(lowerRangeDelta/2)+1

            if (i == tableSize-velocityCycles):
                sampleTable[i+j].keyRangeMax = 127
            else:
                upperRangeDelta = sampleTable[i+velocityCycles].rootNote - sampleTable[i+j].rootNote
                sampleTable[i+j].keyRangeMax = sampleTable[i+j].rootNote+round(upperRangeDelta/2)

            j += 1
        i += velocityCycles

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