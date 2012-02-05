import os
from cbrowse.indexdb import *
import clang.cindex


# Insert 1 def and 3 references
def insertOneDefAndThreeRefs(dbName, filename):
    dbw = IndexDBWriter(dbName)
    dbw.initialize(clang.cindex.CursorKind.get_all_kinds())

    # Insert a variable definition
    defloc = SymbolLocation(filename, 3, 5, 3, 12, 
                            clang.cindex.CursorKind.VAR_DECL)
    dbw.insertDefinitionNode(defloc)
    
    # Insert variable references
    ref1 = SymbolLocation(filename, 4, 5, 4, 12, 
                            clang.cindex.CursorKind.DECL_REF_EXPR)
    ref2 = SymbolLocation(filename, 5, 5, 5, 12, 
                            clang.cindex.CursorKind.DECL_REF_EXPR)
    ref3 = SymbolLocation(filename, 6, 5, 6, 12, 
                            clang.cindex.CursorKind.DECL_REF_EXPR)
    dbw.insertReferenceNode(ref1, defloc)
    dbw.insertReferenceNode(ref2, defloc)
    dbw.insertReferenceNode(ref3, defloc)
    dbw.commit()
    del dbw

def readSymbols(dbName, filename):
    dbr = IndexDBReader(dbName)

    ref1 = SymbolLocation(filename, 4, 5, 4, 12, 
                          clang.cindex.CursorKind.DECL_REF_EXPR)
    cur1 = dbr.getDefinitionNode(ref1)

    print "Definition Node " , cur1
    print "Reference Node " , ref1

    ref2 = SymbolLocation(filename, 5, 5, 5, 12, 
                          clang.cindex.CursorKind.DECL_REF_EXPR)
    cur2 = dbr.getDefinitionNode(ref2)

    print "Cur1 == Cur2 ", (cur1 == cur2)


if __name__ == '__main__':
#    print "/data/work/clang-browser/tests/test.m"
    dbName = "./Output/indexdb_test1.db"
    sourcefile = "/data/work/clang-browser/src/hw.c"

    # Remove the database
    if os.path.exists(dbName):
        os.remove(dbName)
    
    refloc = insertOneDefAndThreeRefs(dbName, sourcefile)

    # Search for references
    readSymbols(dbName, sourcefile)
