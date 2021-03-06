from music21 import converter, corpus
from os import listdir, path, getcwd, chdir
from json import dump
import sys, webbrowser, http.server, socketserver, shutil, pkgutil

def getPaths(directory):
    """
    Accept path to a folder of parsable files and return an array of parsed streams
    Currently only accepts XML and MXL files
    """
    filePaths = []
    fileTypes = ['xml', 'mxl']
    for file in sorted(listdir(directory)):
        fileType = file.split('.')[-1].lower()
        if fileType in fileTypes:
            filePaths.append(path.join(directory, file))
    return filePaths

def checkPath(file):
    fileTypes = ['xml', 'mxl']
    fileType = file.split('.')[-1].lower()
    if fileType not in fileTypes:
        raise ValueError('Input file is not a valid music notation file')
    return [file]

def createStreams(paths):
    """Accept an array of local file paths and return an array of music21 stream objects"""
    streams = []
    for p in paths:
        this = converter.parse(p)
        streams.append(this)
    return streams

def createEntry(thisScore):
    """Accept a music21 score object and return an object that includes an array of notes (with durations and frequencies) and metadata including a title, location, and key"""
    entry = {}
    entry["title"] = thisScore.metadata.title
    entry["location"] = thisScore.metadata.composer
    entry["year"] = thisScore.metadata.movementNumber
    entry["number"] = thisScore.metadata.movementName
#    entry["meter"] = thisScore.recurse().getElementsByClass(meter.TimeSignature)[0]
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
        noteEntry["pitch"] = 'rest'
        if n.isNote:
            noteEntry["frequency"] = n.pitch.frequency
            noteEntry["pitch"] = n.pitch.nameWithOctave
            noteEntry["pitchNum"] = assignPitchNum(n.pitch.nameWithOctave)
        notes.append(noteEntry)
    return notes

def assignPitchNum(n):
    n = str(n)
    if n == "G3":
        pn = 0
    elif n == "A-3":
        pn = 1
    elif n == "A3":
        pn = 2
    elif n == "B-3":
        pn = 3
    elif n == "B3":
        pn = 4
    elif n == "C4":
        pn = 5
    elif n == "D-4":
        pn = 6
    elif n == "D4":
        pn = 7
    elif n == "E-4":
        pn = 8
    elif n == "E4":
        pn = 9
    elif n == "F4":
        pn = 10
    elif n == "G-4":
        pn = 11
    elif n == "G4":
        pn = 12
    elif n == "A-4":
        pn = 13
    elif n == "A4":
        pn = 14
    elif n == "B-4":
        pn = 15
    elif n == "B4":
        pn = 16
    elif n == "C5":
        pn = 17
    elif n == "D-5":
        pn = 18
    elif n == "D5":
        pn = 19
    elif n == "E-5":
        pn = 20
    elif n == "E5":
        pn = 21
    elif n == "F5":
        pn = 22
    elif n == "G-5":
        pn = 23
    elif n == "G5":
        pn = 24
    elif n == "A-5":
        pn = 25
    elif n == "A5":
        pn = 26
    elif n == "B-5":
        pn = 27
    elif n == "B5":
        pn = 28
    else:
        print("ERROR: ", n)
    return pn

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
    resultsDestination = getcwd() + '/results'
    resultsSource = path.dirname(sys.modules['contourviz'].__file__) + '/results'
    resultsExists = path.isdir(resultsDestination)
    if resultsExists:
        shutil.rmtree(resultsDestination)
    shutil.copytree(resultsSource, resultsDestination)
    savePath = 'results/collection_data.json'
    with open(savePath, 'w') as outfile:
        dump(data, outfile)
        print('  --  Data saved to', savePath)
    return

def openWebBrowser():
    """Opens the vizualization in a locally-served web page"""
    print("\nPreparing to serve chart locally on port 9999.")
    print("If you receive an 'port already in use' error, try 'kill 9999' or ")
    print("wait a few moments before running the command again.")
    print("You may also need to reload the website once it loads.\n")
    webbrowser.open('localhost:9999')
    chdir('results/')
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", 9999), Handler)
    print("Serving at port 9999...")
    httpd.serve_forever()

def createDataFromDirectoryCommandLine():
    """Combines function into a complete workflow: generates a set of contour lines derived from a given directory"""
    paths = getPaths(sys.argv[1])
    streams = createStreams(paths)
    entries = getEntries(streams)
    outputData(entries)
    openWebBrowser()
    return

def createDataFromFileCommandLine():
    """Combines function into a complete workflow: generates a set of contour lines derived from a given path"""
    paths = checkPath(sys.argv[1])
    streams = createStreams(paths)
    entries = getEntries(streams)
    outputData(entries)
    openWebBrowser()
    return

def createDataFromDirectory(path):
    """Combines function into a complete workflow: generates a set of contour lines derived from a given directory"""
    paths = getPaths(path)
    streams = createStreams(paths)
    entries = getEntries(streams)
    outputData(entries)
    openWebBrowser()
    return

def createDataFromFile(path):
    """Combines function into a complete workflow: generates a set of contour lines derived from a given path"""
    paths = checkPath(path)
    streams = createStreams(paths)
    entries = getEntries(streams)
    outputData(entries)
    openWebBrowser()
    return
