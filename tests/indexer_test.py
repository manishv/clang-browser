import os, sys
import cbrowse.indexer 
import clang.cindex

from cbrowse.indexdb import *


# Insert 1 def and 3 references
def readVariableDefinitionSymbol(dbr, filename):
    symbolLoc = SymbolLocation(filename, 8, 5, 8, 12)
    print "SymbolLocation: ", symbolLoc

    defNode = dbr.getDefinitionNode(symbolLoc)
    print "Definition Node", defNode
    
    
def readFunctionCallSymbol(dbr, filename):

    # Reference is location of call to function foo
    refSymbol = SymbolLocation(filename, 9, 7, 9, 13)
    print "Reference Symbol", refSymbol

    # def symbol should be the definition of function foo
    defNode = dbr.getDefinitionNode(refSymbol)
    print "Definition Node " , defNode

    symbolLoc = SymbolLocation(filename, 3, 1, 6, 2, 
                               clang.cindex.CursorKind.FUNCTION_DECL)
    print "Correct Definition Symbol : %s" %\
        (IndexDBReader.getSymbol(dbr, symbolLoc) == defNode.defsymbol)

        
if __name__ == '__main__':
    #sourcefile = "/data/work/clang-browser/tests/indexer_test.c"
    sourcefile = sys.argv[1][:-1]+'c'
    dbName = sys.argv[2]

    # Remove the database
    if os.path.exists(dbName):
        os.remove(dbName)
    #Check that the source file exists
    assert os.path.exists(sourcefile)    

    indexer = cbrowse.indexer.Indexer(dbName)
    indexer.index(sourcefile)
    
    del indexer

    # Search for the variable definition symbol
    # dbReader = IndexDBReader(dbName);
    # readVariableDefinitionSymbol(dbReader, sourcefile)

    # Search for the function call symbol
#    readFunctionCallSymbol(dbReader, sourcefile)

