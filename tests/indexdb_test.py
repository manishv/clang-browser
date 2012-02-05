from cbrowse.indexdb import *
import clang.cindex


# This inserts one definition and one reference symbol It then prints out the
# definition symbol from the reference symbol. The test also check classes for
# accessing reading and writing of index database

def insertSymbols(dbName, filename):
    dbw = IndexDBWriter(dbName)
    dbw.initialize(clang.cindex.CursorKind.get_all_kinds())

    # Insert a variable definition
    defloc = SymbolLocation(filename, 3, 12, 3, 5, 
                            clang.cindex.CursorKind.VAR_DECL)
    dbw.insertDefinitionNode(defloc)
    
    # Insert variable references
    refloc = SymbolLocation(filename, 4, 12, 4, 5, 
                            clang.cindex.CursorKind.DECL_REF_EXPR)
    dbw.insertReferenceNode(refloc, defloc)
    dbw.commit()
    del dbw
    return refloc

def readSymbols(dbName, filename):
    dbr = IndexDBReader(dbName)

    refloc = SymbolLocation(filename, 4, 12, 4, 5, 
                            clang.cindex.CursorKind.DECL_REF_EXPR)
    cur = dbr.getDefinitionNode(refloc)

    print "Definition Node %s for Reference Node %s" % (cur, refloc)


if __name__ == '__main__':
#    print "/data/work/clang-browser/tests/test.m"
    dbName = "./Output/indexdb_test.db"
    sourcefile = "/data/work/clang-browser/src/hw.c"
    
    refloc = insertSymbols(dbName, sourcefile)

    # Search for references
    readSymbols(dbName, sourcefile)
