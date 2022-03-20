#!/usr/bin/env python3

import wave
import pathlib
import sys
from dataclasses import dataclass

def main():
    if(len(sys.argv) != 2):
        print("Erorr: Expected 1 argument but found",len(sys.argv)-1)
        if(len(sys.argv) == 1):
            print("Error: Please provide wav folder path as argument!")
        exit(1)

    wavDirectory = pathlib.Path(sys.argv[1])

    if(wavDirectory.is_dir() == False):
        print("Error: path is not a directory!")
        exit(1)
    samplerName = wavDirectory.name
    

    print(samplerName)

    @dataclass
    class Sample:
        fileName: pathlib.PosixPath
        rootNote: int
        velocity: int

    sampleTable = []
    for wav in wavDirectory.glob("*.wav"):
        rootNoteVelocity = wav.stem[len(samplerName):]
        rootNoteStr = rootNoteVelocity.split("_")[1]
        velocityStr = rootNoteVelocity.split("_")[2]
        sampleTable.append(Sample(wav.name, rootNoteStr, velocityStr))
    print(sampleTable[-1])
    print(len(sampleTable))

    exit(0)

    w = wave.open("wavs/C3.wav", 'rb')
    print(w.getnframes())
    
    w.close()
    exit(0)

if __name__ == '__main__':
    main()