#!/usr/bin/python
# encoding: utf-8


config = [
    {'path': "1T-4t 3-alles F20.gcode", 'start': 0, 'stop': 840},
    {'path': "1T-4t 3-alles F100.gcode", 'start': 840, 'stop': None}
]


def findStartLine(fileConfig):
    if fileConfig['start'] == 0:
        return 0
    else:
        return findLayerLine(fileConfig['path'], fileConfig['start'])


def findLayerLine(path, layer):
    lines = open(path).readlines()
    for index, line in enumerate(lines):
        if "LAYER:" + `layer` in line:
            return index

    raise ValueError('Following layer could not be found', layer)


def parseExtrusion(line):
    extrusion = line.split(" ")[-1]
    value = float(extrusion[1:])
    return value


def doesLineContainExtrusion(line):
    return line.startswith("G") and "E" in line


def findLastExtrusionBeforeLayer(path, lastLayer):
    lastLayerIndex = findLayerLine(path, lastLayer)
    lines = open(path).readlines()
    for line in reversed(lines[0:lastLayerIndex]):
        if doesLineContainExtrusion(line):
            return parseExtrusion(line)
    raise ValueError('No last extrusion value could be found for file before layer', path, lastLayer)


def replaceExtrusion(line, currentFileLastExtrusion, previousFileLastExtrusion):
    diff = currentFileLastExtrusion - parseExtrusion(line)
    newExtrusion = previousFileLastExtrusion - diff
    return " ".join(line.split(" ")[:-1]) + " E" + '{0:.5f}'.format(newExtrusion) + "\n"


def appendToFile(outputFile, fileConfig, currentFileLastExtrusion, previousFileLastExtrusion):
    lines = open(fileConfig['path']).readlines()
    startLineIndex = findStartLine(fileConfig)

    if fileConfig['stop'] == None:
        endLineIndex = len(lines)
    else:
        endLineIndex = findLayerLine(fileConfig['path'], fileConfig['stop'])

    print "startLineIndex: " + `startLineIndex`
    print "endLineIndex: " + `endLineIndex`
    print ""

    for index, line in enumerate(lines):
        if startLineIndex <= index < endLineIndex:
            # print "writing line " + `index`
            if currentFileLastExtrusion != None and previousFileLastExtrusion != None and doesLineContainExtrusion(line):
                line = replaceExtrusion(line, currentFileLastExtrusion, previousFileLastExtrusion)

            outputFile.write(line)


outputFile = open("output.gcode", "w")

for index, fileConfig in enumerate(config):
    previousFileLastExtrusion = None;
    currentFileLastExtrusion = None;

    if index > 0:
        previousConfig = config[index - 1]
        previousFileLastExtrusion = findLastExtrusionBeforeLayer(previousConfig['path'], previousConfig['stop'])
        currentFileLastExtrusion = findLastExtrusionBeforeLayer(fileConfig['path'], fileConfig['start'])

    print "File: " + `fileConfig['path']`
    print "previousFileLastExtrusion: " + `previousFileLastExtrusion`
    print "currentFileLastExtrusion: " + `currentFileLastExtrusion`

    appendToFile(outputFile, fileConfig, currentFileLastExtrusion, previousFileLastExtrusion)

print "DONE"
outputFile.close()
