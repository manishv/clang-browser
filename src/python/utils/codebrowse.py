#!/usr/bin/env python

import os
import optparse
import sys

import cbrowse.indexer
import cbrowse.indexdb
# import lit.ProgressBar
DEFAULT_DBNAME="symbols.db"


def buildIndexDatabase(indexer, filename, args):
    # tc = ProgressBar.TerminalController()
    # progressBar = ProgressBar.ProgressBar(tc, "code browser")
    indexer.index(filename, args)

def createSymbol(args):
    try:
        loc = cbrowse.indexdb.SymbolLocation(args[0], int(args[1]), 
                                             int(args[2]),
                                             int(args[3]), 
                                             int(args[4]))
    except:
        print "Unexpected Error", sys.exc_info()[0]
        sys.stderr.write("Incorrect argument specified\n")
        sys.stderr.write(helpString())
        exit(1)
    return loc
        

def helpString():
    s  = "available commands are: \n"
    s += "   build: builds the index database \n"
    s += "   find-def: find the definition \n"
    s += "   find-ref: find all references to the symbol \n"
    
    return s

def parseCmd(args):
    cmd = args[0]
    if cmd == "build":
        cmdArgs = args[1:]
    elif cmd == "find-def" or \
            cmd == "find-ref" :
        cmdArgs = [ createSymbol(args[1:]) ]
    else:
        sys.stderr.write("Incorrect command specified\n")
        sys.stderr.write(helpString())
        exit(1)
    return (cmd, cmdArgs)

def argParser():
    global DEFAULT_DBNAME
    parser = optparse.OptionParser("Usage: cbrowse [options]"\
                                       " <cmd> <cmd_args> \n" + 
                                   helpString())
    parser.add_option("", "--dbname", dest="database", #default=DEFAULT_DBNAME,
                      help="Name of index database (default: %s)" % 
                      DEFAULT_DBNAME)
    parser.disable_interspersed_args()

    (opts, args) = parser.parse_args()
    if opts.database == None:
        opts.database = os.environ.get("CBROWSE_DATABASE", DEFAULT_DBNAME)

    if len(args) < 2:
        sys.stderr.write("Error in argument parsing\n")
        sys.stderr.write(helpString())
        exit(1)
    (cmd, cmdArgs) = parseCmd(args)

    return (opts, cmd, cmdArgs)


def getDefinition(dbReader, loc):
    defNode = dbReader.getDefinitionNode(loc)
    print "Definition Node: ", defNode

def getReferences(dbReader, loc):
    defNode = dbReader.getDefinitionNode(loc)
    refNodes = dbReader.getReferenceNodes(defNode.getLocation())
    print "Reference Nodes: "
    for r in refNodes:
        print r


def main():
    (opts, cmd, cmdArgs) = argParser()

    dbName = opts.database
    if not os.path.exists(os.path.dirname(os.path.abspath(dbName))):
        sys.stderr.write("Error: cannot access %s: No such database file or directory\n" 
                         % dbName)
        exit(1)
    
    filename = cmdArgs[0]

    if cmd=="build":
        indexer = cbrowse.indexer.Indexer(dbName)
        buildIndexDatabase(indexer, filename, cmdArgs[1:])
    elif cmd == "find-def":
        dbReader = cbrowse.indexdb.IndexDBReader(dbName)
        getDefinition(dbReader, cmdArgs[0])
    elif cmd == "find-ref":
        dbReader = cbrowse.indexdb.IndexDBReader(dbName)
        getReferences(dbReader, cmdArgs[0])
if __name__ == '__main__':
    main()
