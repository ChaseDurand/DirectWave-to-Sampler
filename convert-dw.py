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
    cycle: int
    zoneMin: int
    zoneMax: int
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
        fileTail = wav.stem.split(" ")[-1].split("_")

        # Confirm file name tail is either:
        #   Layers_rootNote_velocity
        # or
        #   #xCycles_rootNote_velocity_cycle
        if(len(fileTail) != 3 and len(fileTail) != 4):
            print("Error! Unable to parse wav filename:", wav.stem)
            exit(1)

        robinCycles = fileTail[0]
        if(robinCycles != "Layers"):
            # Generate round robin cycle ranges
            cycle = int(fileTail[3]) - 1
            totalCycles = int(robinCycles.split("x")[0])
            k, m = divmod(len(range(0, 128, 1)), totalCycles)
            cycleRange = list((range(0, 128, 1)[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(totalCycles)))[cycle]
            cycle = str(fileTail[3])
        else:
            totalCycles = 1
            cycle = 1
            cycleRange=[0, 127]

        rootNoteStr = fileTail[1]
        velocityStr = int(fileTail[2])
        frameEnd = wave.open(str(wav), 'rb').getnframes() -1
        sampleTable.append(Sample(wav,
                                  wav.name,
                                  getNoteFromStr(rootNoteStr),
                                  0,
                                  0,
                                  velocityStr,
                                  0,
                                  0,
                                  cycle,
                                  cycleRange[0],
                                  cycleRange[-1],
                                  frameEnd))

    # Sort by root note, then velocity, then round robin cycle
    sampleTable = sorted(sampleTable, key = lambda x: (x.rootNote, x.velocityRoot, x.cycle))

    # Determine velocity cycles
    velocityCycles = 1
    i = 0
    while(i < len(sampleTable)):
        if(i != 0):
            if((sampleTable[i].rootNote == sampleTable[0].rootNote)\
                and (sampleTable[i].velocityRoot != sampleTable[0].velocityRoot)):
                velocityCycles += 1
            else:
                break
        i += 1
    i = 0

    tableSize = len(sampleTable)
    print(tableSize, velocityCycles, totalCycles)
    while(i != tableSize):
        j = 0
        while(j < velocityCycles):
            k = 0
            while(k < totalCycles):
                # Handle velocity ranges
                if (j == 0):
                    sampleTable[i+j+k].velocityMin = 0
                else:
                    lowerRangeDelta = sampleTable[i+j].velocityRoot - sampleTable[i+j-1].velocityRoot
                    sampleTable[i+j+k].velocityMin = sampleTable[i+j].velocityRoot-ceil(lowerRangeDelta/2)+1

                if (j == velocityCycles-1):
                    sampleTable[i+j+k].velocityMax = 127
                else:
                    upperRangeDelta = sampleTable[i+j+1].velocityRoot - sampleTable[i+j].velocityRoot
                    sampleTable[i+j+k].velocityMax = sampleTable[i+j].velocityRoot+round(upperRangeDelta/2)
                
                # Handle note ranges
                if (i == 0):
                    sampleTable[i+j+k].keyRangeMin = 0
                else:
                    lowerRangeDelta = sampleTable[i+j].rootNote - sampleTable[(i+j)-velocityCycles].rootNote
                    sampleTable[i+j+k].keyRangeMin = sampleTable[i+j].rootNote-ceil(lowerRangeDelta/2)+1

                if (i == tableSize- (velocityCycles * totalCycles)):
                    sampleTable[i+j+k].keyRangeMax = 127
                else:
                    upperRangeDelta = sampleTable[i+velocityCycles].rootNote - sampleTable[i+j].rootNote
                    sampleTable[i+j+k].keyRangeMax = sampleTable[i+j].rootNote+round(upperRangeDelta/2)
                k += 1
            j += totalCycles
        i += (velocityCycles * totalCycles)

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