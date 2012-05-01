#!/usr/bin/env python
#-*- python -*-

import os, sys

def getIndexerScript():
    curPath = os.path.dirname(os.path.realpath(__file__))
    indexerPath = os.path.join(curPath, "codebrowse.py")
    print indexerPath
    if not os.path.exists(indexerPath):
        sys.stderr.write("Unable to find indexer script at %s\n" % indexerPath)
        sys.exit(1)
    return indexerPath

def checkOrSetEnvVariable():
    """ This method checks if CBROWSE_DATABASE enviornment variable is defined
    by the user. If not then it defines the enviornment variable to index.db
    """
    envVar = os.environ.get("CBROWSE_DATABASE")
    if not envVar:
        os.environ["CBROWSE_DATABASE"] = "index.db"

def isSourceFile(string):
    """Returns true if the argument is a C/C++ source file name, 
    otherwise returns false
    """
    dotLoc = string.rfind('.')
    if dotLoc == -1:
        return False
    ext = string[dotLoc+1:]
    return ext in ( "c", "cc", "cp", "cxx", "cpp", "CPP", "c++", "C" )


def collectArgs(argsList):
    """Parses arglist, which is a command line passed to a compiler,
    to collect the list of source-files passed on the command line. It 
    returns a tuple consisting of command line options and a list of
    source-files.
    """

    filesList   = [ a for a in argsList if isSourceFile(a) ]
    remArgsList = [a for a in argsList if a not in filesList ]

    #convert files into their full-path names
    filesList = [ os.path.realpath(a) for a in filesList ]

    return (remArgsList, filesList)

import codebrowse
def main():
    (args, files) = collectArgs(sys.argv[1:])
    indexerScript = getIndexerScript()
    checkOrSetEnvVariable()

    print os.environ.get("CBROWSE_DATABASE")
    print args
    print files
    if not files:
        print "dont call cbrowse"


if __name__ == '__main__':
    main()

