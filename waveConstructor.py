# Wave Constructor: Generate waveJSON based on text description
#   Copyright (C) 2020      Jading Tsunami
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import string

class waveConstructor:

    # class data
    declarative_keywords = ['group', 'wave']
    modifier_keywords = ['period', 'phase']

    def __init__(self):
        self.groups = []
        self.group_ends = []
        self.waves = []

        # array of string edge assignments
        self.edges = []
        self.unbuilt_edges = []
        # list of which edges are not used already
        self.unused_node_markers = list(string.ascii_letters)
        self.frame = 0
        self.parser_done = False

    def reset(self):
        self.__init__()

    def nextFrame(self):
        self.frame += 1

    def getWave(self, w):
        if w:
            for ww in self.waves:
                if ww.name == w:
                    return ww

        w1 = Wave()
        w1.name = w
        self.waves.append(w1)
        return w1


    def getNextUnusedNodeMarker(self):
        assert len(self.unused_node_markers) > 0, "No more node markers left!"
        return self.unused_node_markers.pop(0)


    def getNodeMarker(self, wave, edgeFrame):
        for n in wave.node:
            if n[0] == edgeFrame:
                return n[1]
        # if we made it here, there isn't one, so it needs to be added.
        nodeMarker = self.getNextUnusedNodeMarker()
        wave.addEdgeNode(edgeFrame, nodeMarker)
        return nodeMarker

    def parse(self, tokens):
        # will eventually refactor this
        # skip blanks and comments
        if len(tokens) == 0 or tokens[0][0] == "#":
            return

        # identify the keyword token
        keyword = tokens[0]

        if keyword.startswith('.'):
            for i in range(len(keyword)):
                if keyword[i] == '.':
                    self.nextFrame()

        elif keyword == 'group':
            self.groups.append((tokens[1], len(self.waves)))
        elif keyword == 'end':
            self.group_ends.append(len(self.waves))
        elif keyword == 'wave':
            newWave = self.getWave(tokens[-1])
            if len(tokens) > 2:
                newWave.longname = tokens[1]

        else:
            # other commands are assignments, modifiers or edges
            assert len(tokens) >= 3, "Bad line parse: %s" % str(tokens)
            arg1 = tokens[0]
            op = tokens[1]
            arg2 = tokens[2]
            arg3 = False
            if len(tokens) > 3:
                arg3 = tokens[-1].strip()

            if isEquality(op):
                # assignment
                v = str(arg2)

                if arg1 == "all" and isValidWaveSymbol(v):
                    for w in self.waves:
                        if w.name:
                            w.addToWave(self.frame, v)
                    return

                w1 = self.getWave(arg1)

                if isValidWaveSymbol(v):
                    # shouldn't hit this since you'd have to
                    # stumble on the exact sequence, but it
                    # could happen
                    assert len(v) == 1, "Too many characters in assignment: %s" % str(tokens)
                    w1.addToWave(self.frame, v)
                elif v[0] == 'n' and v[1].isalpha():
                    w1.addEdgeNode(self.frame, v[1])
                    if v[1] in self.unused_node_markers:
                        self.unused_node_markers.remove(v[1])
                else:
                    # assume it's data, and assign it accordingly
                    w1.addToWave(self.frame, '2')
                    w1.addData(v)

                if arg3:
                    w1.addData(arg3)
                elif isDataWaveSymbol(v):
                    w1.addData("")


            elif isArrow(op):
                # edge
                if isEdgeLetter(arg1) and isEdgeLetter(arg2):
                    e = str(arg1)
                    e += str(op)
                    e += str(arg2)
                    if arg3:
                        e += " "
                        e += str(arg3)
                    self.edges.append(e)
                    if arg1 in self.unused_node_markers:
                        self.unused_node_markers.remove(arg1)
                    if arg2 in self.unused_node_markers:
                        self.unused_node_markers.remove(arg2)
                else:
                    # must be of the form wave -> wave
                    # both waves must already exist
                    w1 = self.getWave(arg1)
                    w2 = self.getWave(arg2)

                    f1 = findWaveChange(w1.wave, self.frame)

                    if f1 < 0 or f1 > self.frame:
                        f1 = self.frame

                    e1 = f1
                    e2 = self.frame

                    if not arg3:
                        arg3 = ""
                    self.unbuilt_edges.append([(w1,e1),op,(w2,e2),arg3])

            elif isModifier(op):
                # wave modifier
                w1 = self.getWave(arg1)
                # FIXME: This needs to be in the parser
                (arg2,arg3) = arg2.strip().split(" ",2)
                assert w1 and arg2 and arg3, "Bad modifier assignment: %s" % str(tokens)
                w1.addModifier(arg2,arg3)

    def parseLine(self,line):
        tokens = self.tokenize(line)
        self.parse(tokens)

    def runParser(self,source,isFile=False):
        if isFile:
            self.__runParserOnFile(source)
        else:
            self.__runParserOnString(source)
        self.parser_done = True

    def __runParserOnString(self,instring):
        for line in instring.split('\n'):
            self.parseLine(line)

    def __runParserOnFile(self,infile):
        f = open(infile, "r")
        for line in f:
            self.parseLine(line)
        f.close()

    def buildRunner(self,name,runner,firstChar='x'):
        s = str(name) + ": \""
        c = runner.pop(0)
        for i in range(self.frame+1):
            # assumes wave nodes are frames in order
            if c and c[0] == i:
                s += c[1]
                if len(runner) > 0:
                    c = runner.pop(0)
                else:
                    c = None
            elif i == 0:
                s += firstChar
            else:
                s += '.'
        s += "\""
        return s

    def buildWave(self,w):
        s = "{"

        if w.name:
            s += "\"name\": %s" % formatSpanString(w.getName())

        if w.wave:
            s += ", "
            s += self.buildRunner("\"wave\"",w.wave)

        if w.node:
            s += ", "
            s += self.buildRunner("\"node\"",w.node,'.')


        if w.data:
            s += ", "
            s += "\"data\": ["
            first_data = True
            for d in w.data:
                if first_data:
                    first_data = False
                else:
                    s += ','
                s += formatSpanString(d)
            s += "]"

        if w.modifiers:
            for m in w.modifiers.keys():
                s += ", "
                s += "\"" + str(m) + "\": " + str(w.modifiers[m])
        s += "}"
        return s

    def generateWavedrom(self,inputSource,isFile=False):
        self.reset()
        self.runParser(inputSource,isFile)
        return self.generateWaveJSON()


    def generateWaveJSON(self):
        assert self.parser_done, "Error: Run parser before generating waveform."

        # build edges, if necessary
        for e in self.unbuilt_edges:
            # unpack unbuilt edge
            wave1 = e[0][0]
            edgeFrame1 = e[0][1]
            arrow = e[1]
            wave2 = e[2][0]
            edgeFrame2 = e[2][1]
            label = e[3]

            # get or add node markers
            edgeNode1 = self.getNodeMarker(wave1,edgeFrame1)
            edgeNode2 = self.getNodeMarker(wave2,edgeFrame2)

            newEdge = str(edgeNode1) + str(arrow) + str(edgeNode2)
            if label:
                newEdge += str(" ") + str(label)
            self.edges.append(newEdge)

        # preamble
        f = "{\"signal\": [\n"

        # build waves
        wave_count = 0
        first_group = True
        first_wave = True
        for w in self.waves:

            # group opens
            while len(self.groups) > 0 and self.groups[0][1] == wave_count:
                first_wave = True
                if first_group:
                    first_group = False
                else:
                    f += ","

                g = self.groups.pop(0)
                f += "\n[\""
                f += str(g[0])
                f += "\",\n"

            if first_wave:
                first_wave = False
            else:
                f += ","
                f += "\n"
            f += self.buildWave(w)
            wave_count += 1

            # group closes
            while len(self.group_ends) > 0 and self.group_ends[0] == wave_count:
                self.group_ends.pop(0)
                f += "\n]\n"


        f += "]"
        f += "\n"

        if self.edges:
            f += ", \"edge\": ["
            first = True
            for e in self.edges:
                if first:
                    first = False
                else:
                    f += ','
                f += '\"'
                f += str(e)
                f += '\"'
            f +="]"

        # postamble
        f += "}"
        return f

    def tokenize(self,line):
        wordsplit = [x.strip() for x in line.split()]
        if len(wordsplit) > 0 and wordsplit[0] in self.declarative_keywords:
            decl_split = [wordsplit[0]]
            # TODO: Allow escaped quotes
            string_split = line.split("\"")
            decl_split.append(string_split[1].strip())
            if len(string_split) > 2 and string_split[-1].strip():
                decl_split.append((string_split[-1][len(" as"):]).strip())
            return decl_split

        elif ':' in line:
            colonSplit = line.split(":",1)
            if len(colonSplit) > 1:
                finalSplit = colonSplit[0].split()
                finalSplit.append(":")
                finalSplit.append(colonSplit[1])
                return finalSplit

        elif len(wordsplit) > 2 and wordsplit[1] == "=":
            eqSplit = [ x.strip() for x in line.split("=") ]
            return [eqSplit[0],"=",eqSplit[1]]

        return line.split()


class Wave:

    def __init__(self):
        self.name = ''
        self.longname = None
        self.wave = []
        self.node = []
        self.data = []
        self.modifiers = {}
        self.edge_num = 0

    def getName(self):
        if self.longname:
            return self.longname
        return self.name

    def addToWave(self,frame,value):
        # remove any updates that match the given
        # frame. Only 1 update per frame is allowed.
        for w in self.wave:
            if len(w) > 0 and w[0] == frame:
                self.wave.remove(w)
        self.wave.append( ( frame, value ) )

    def addData(self,d):
        self.data.append(d)

    def addModifier(self,modifier,value):
        self.modifiers[modifier] = value

    def addEdgeNode(self, frame, edge):
        self.node.append( (frame,edge) )
        self.node.sort(key=lambda t: t[0])





def parseArgs(args):
    if len(args) != 3:
        print "Usage: " + args[0] + " <infile> <outfile>"
        return (-1,-1)

    return (str(args[1]),str(args[2]))

# Helper Functions

def findWaveChange(wave,endFrame):
    """
    Find most recent change in a wave definition.
    """
    loc = -1
    for c in wave:
        if c[0] > endFrame:
            return loc
        elif c[1] != '|':
            loc = c[0]
    return loc


def isArrow(tok):
    arrow_starters = ['-','~','|','<']
    if tok[0] in arrow_starters:
        return True
    return False

def isEdgeLetter(tok):
    return len(tok) == 1 and tok.isalpha()

def isModifier(tok):
    return tok == ":"

def isEquality(tok):
    return tok == "="

def isValidWaveSymbol(v):
    return v in "01.zx=ud23456789|pPnNlLHh"

def isDataWaveSymbol(v):
    return v in "23456789"

def formatSpanString(s):
    s = s.strip()
    if not (s.startswith('[') and s.endswith(']')):
        return "\"" + s + "\""
    else:
        return s.replace("\'","\"")
        

def writeFile(outfile,writeData):
    with open(outfile,"w") as f:
        f.write("<html><head>\n")
        f.write("<script src=\"http://wavedrom.com/skins/default.js\" type=\"text/javascript\"></script>\n")
        f.write("<script src=\"http://wavedrom.com/wavedrom.min.js\" type=\"text/javascript\"></script>\n")
        f.write("</head>\n")
        f.write("<body onload=\"WaveDrom.ProcessAll()\">\n")
        f.write("<script type=\"WaveDrom\">\n")
        f.write(writeData)
        f.write("\n</script>\n")
        f.write("</body>\n")
        f.write("</html>\n")

def main():
    import sys
    (infile,outfile) = parseArgs(sys.argv)
    wc = waveConstructor()
    finalWave = wc.generateWavedrom(infile,isFile=True)
    print str(finalWave)
    writeFile(outfile,finalWave)


if __name__ == "__main__":
    # execute only if run as a script
    main()
