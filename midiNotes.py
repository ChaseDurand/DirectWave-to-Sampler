notes = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11
}

# Given a note in string format Note+Octave,
# return the MIDI note (0-127)
def getNoteFromStr(noteStr: str) -> int:
    key = noteStr[:-1]
    octave = int(noteStr[-1])
    note = (12 * (octave+1)) + notes[key]
    return note
    