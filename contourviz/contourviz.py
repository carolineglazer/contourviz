from music21 import corpus
from os import listdir
from json import dump
import sys

def getPaths(directory):
    """Accept path to a folder of parsable files and return an array of parsed streams"""
    return listdir(directory)

def createStreams(paths):
    """Accept an array of local file paths and return an array of music21 stream objects"""
    streams = []
    for p in paths:
        this = corpus.parse(p)
        streams.append(this)
    return streams

def createEntry(thisScore):
    """Accept a music21 score object and return an object that includes an array of notes (with durations and frequencies) and metadata including a title"""
    entry = {}
    entry["metadata"] = thisScore.metadata.title
    entry["notes"] = getNotes(thisScore)
    return entry

def getNotes(thisScore):
    """Accept a music21 score object and return an array of all note durations and frequencies"""
    notes = []
    recursiveScore = thisScore.recurse()
    allNotes = recursiveScore.notes
    initialRestOffset = allNotes[0].offset
    for n in allNotes:
        noteEntry = {}
        noteEntry["offset"] = float(n.getOffsetBySite(recursiveScore)) - initialRestOffset
        noteEntry["duration"] = float(n.quarterLength)
        noteEntry["frequency"] = 'rest'
        if n.isNote:
            noteEntry["frequency"] = n.pitch.frequency
        notes.append(noteEntry)
    return notes

def getEntries(collection):
    """Accept an array of music21 streams and write a JSON object of created data entries"""
    data = []
    total = len(collection)
    for i, s in enumerate(collection):
        data.append(createEntry(s))
    	progress = i * 1.0 / total * 100
        sys.stdout.write("  --  Processing melodies: %d%%\r" % progress)
        sys.stdout.flush()
    return data

def outputData(data):
    """Accepts formatted data object and outputs it to a JSON file for the web interface"""
    savePath = 'contourviz/results/collection_data.json'
    with open(savePath, 'w') as outfile:
        dump(data, outfile)
        print '  --  Data saved to', savePath
    return

def createDataFromDirectory(path):
    """Combines function into a complete workflow"""
    paths = getPaths(path)
    streams = createStreams(paths)
    entries = getEntries(streams)
    outputData(entries)
    return
