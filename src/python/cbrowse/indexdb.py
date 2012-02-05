import collections
import sys

import clang.cindex
import storm.exceptions
from storm.locals import *
import storm.tracer

class SymbolKind(object):
    __storm_table__ = "symbolkind"
    id    = Int(primary=True)
    name  = Unicode()
    value = Int()
    
    def __init__(self, name, value):
        self.name  = unicode(name)
        self.value = value
    
    def __str__(self):
        return "< id: %r name: %r value: %d >" % (self.id, self.name, 
                                                  self.value)
    @staticmethod
    def createTableString():
        return "CREATE TABLE IF NOT EXISTS symbolkind "\
            "(id INTEGER PRIMARY KEY, name VARCHAR, value INTEGER)"

class FileName(object):
    __storm_table__ = "filename"
    id = Int(primary=True)
    name = Unicode()
    
    def __init__(self, filename):
        assert (filename != None)
        self.name = unicode(filename)
    
    def __str__(self):
        return "< id: %r filename: %r >" % (self.id, self.name)
    
    @staticmethod
    def createTableString():
        return "CREATE TABLE IF NOT EXISTS filename "\
            "(id INTEGER PRIMARY KEY, name VARCHAR)"

SymbolLocation = collections.namedtuple('SymbolLocation', 
                                        'filename, sl, sc, el, ec, nodekind')

class Symbol(Storm):
    __storm_table__ = "symbol"
    filename_id   = Int()
    filename      = Reference(filename_id, FileName.id)
    symbolkind_id = Int()
    symbolkind    = Reference(symbolkind_id, SymbolKind.id)
    start_line    = Int()
    start_col    = Int()
    end_line      = Int()
    end_col      = Int()
    definition_id = Int()
    definition = Reference(definition_id, "DefinitionSymbol.id")
    id = Int(primary=True)
    
    def __init__(self, location, 
                 filename_id=None, symbolkind_id=None):
        self.start_line    = location.sl
        self.start_col     = location.sc
        self.end_line      = location.el
        self.end_col       = location.ec
        self.filename_id   = filename_id
        self.symbolkind_id = symbolkind_id

    def __str__(self):
        return "<id : %r kind: %s filename: %s [%d:%d - %d:%d] >" % \
            (self.id, self.symbolkind.name, self.filename.name, 
             self.start_line, self.start_col, 
             self.end_line, self.end_col)

    @staticmethod
    def createTableString():
        return "CREATE TABLE IF NOT EXISTS symbol "\
            "(id INTEGER PRIMARY KEY, "\
            "filename_id INTEGER, symbolkind_id INTEGER, "\
            "definition_id INTEGER, "\
            "start_line INTEGER, start_col INTEGER, "\
            "end_line INTEGER, end_col INTEGER)"

class DefinitionSymbol(Storm):
    __storm_table__ = "defsymbol"
    id = Int(primary=True)
    defsymbol_id = Int()
    defsymbol    = Reference(defsymbol_id, Symbol.id)
    references   = ReferenceSet(id, Symbol.definition_id)

    def __init__(self):
        pass

    def __str__(self):
        refstr = [str(r) for r in self.references]
        string = "< " + str(self.defsymbol) + "Refs: " + ",".join(refstr) + " >"
        return string

    @staticmethod
    def createTableString():
        return "CREATE TABLE IF NOT EXISTS defsymbol "\
            "(id INTEGER PRIMARY KEY, defsymbol_id INTEGER)"
                                 

#TODO: We need an exception class to throw all the errors
class IndexDB:
    dbtype    = "sqlite"
    dbtimeout = "2"
    def __init__(self, dbname):
        self.dbname  = dbname
        self.db = create_database(self.dbtype+":"+self.dbname+
                                  "?timeout="+self.dbtimeout)
    
        try:
            self.stormdb = Store(self.db)
        except storm.exceptions.StormError:
            sys.stderr.write("Error: in accessing the database (%s)\n" %
                             self.dbname)
            sys.exit(1)

        #Create all the unders
        self.stormdb.execute(SymbolKind.createTableString())
        self.stormdb.execute(FileName.createTableString())
        self.stormdb.execute(Symbol.createTableString())
        self.stormdb.execute(DefinitionSymbol.createTableString())

        #Variable to cache the last filename
        self.lastfile = None        

    def initialize(self, symbolKinds):
        #Populate the data in SymbolKind, if it is already not created
        try:
            results = self.stormdb.get(SymbolKind, 1)
            if not results:
                for kind in symbolKinds:
                    self.stormdb.add(SymbolKind(kind.name, kind.value))
                self.stormdb.commit()
        except storm.exceptions.StormError:
            self.stormdb.rollback()
            sys.stderr.write("Error: writing to the database (%s)\n" % 
                             self.dbname)
            sys.exit(1)
        return self

    def commit(self):
        self.stormdb.commit()

    def getFileName(self, name):
        unicodeName = unicode(name)
        result  = self.stormdb.find(FileName, FileName.name == unicodeName)
        newfile = None
        if not result.is_empty():
            assert (result.count()==1)
            newfile = result.one()
        return newfile
            
    def getNodeKind(self, nodeKind):
        result = self.stormdb.find(SymbolKind, SymbolKind.value == 
                                   nodeKind.value)
        assert (not result.is_empty())
        return result.one()

    def getSymbol(self, location):
        fileClass = self.getFileName(location.filename)
        assert(fileClass != None)
        fileId = fileClass.id
        result = self.stormdb.find(Symbol, 
                                    Symbol.filename_id == fileId,
                                    Symbol.start_line  == location.sl,
                                    Symbol.start_col   == location.sc,
                                    Symbol.end_line    == location.el,
                                    Symbol.end_col     == location.ec)
        if not result.is_empty():
            assert(result.count()==1)
            return result.one()
        return None
        
class IndexDBWriter(IndexDB):
    
    def getOrInsertFileName(self, name):
        result = self.getFileName(name)
        newfile = None
        if result == None:
            newfile = FileName(unicode(name))
            self.stormdb.add(newfile)
            self.stormdb.flush()
        else:
            newfile = result
        return newfile

    #TODO: Need to implement rollback and errorhandling
    def insertDefinitionNode(self, location):
        fileId     = self.getOrInsertFileName(location.filename).id
        nodeKindId = self.getNodeKind(location.nodekind).id
        assert (fileId != None and nodeKindId != None)

        symbol = self.getSymbol(location)
        if symbol == None :
            symbol = Symbol(location, fileId, nodeKindId)
            self.stormdb.add(symbol)
            self.stormdb.flush()
            defSymbol = DefinitionSymbol()
            defSymbol.defsymbol = symbol
            defSymbol.references.add(symbol)
            self.stormdb.flush()
        return symbol

    #TODO: Need to implement rollback and errorhandling
    def insertReferenceNode(self, location, defLocation):
        fileId     = self.getOrInsertFileName(location.filename).id
        nodeKindId = self.getNodeKind(location.nodekind).id
        assert (fileId != None and nodeKindId != None)
        
        symbol = self.getSymbol(location)
        if symbol == None:
            symbol = Symbol(location, fileId, nodeKindId)
            self.stormdb.add(symbol)
            self.stormdb.flush()
            defSymbol = self.getSymbol(defLocation).definition
            defSymbol.references.add(symbol)
            self.stormdb.flush()
        return symbol

class IndexDBReader(IndexDB):
        
    def getDefinitionNode(self, refLocation):
        refSymbol = self.getSymbol(refLocation)
        if refSymbol != None:
            defSymbol = refSymbol.definition
            return defSymbol
        sys.stderr.write("Error: Symbol not found (%s)" % refLocation)
        return None

    def getReferenceNodes(self, defLocation):
        symbol = self.getSymbol(defLocation)
        if symbol != None:
            defSymbol = symbol.definition
            assert (defSymbol!=None)
            return defSymbol.references

        sys.stderr.write("Error: Symbol not found (%s) " % defLocation)
        return None
    
#TODO: Decide how does the API returns SymbolLocation 
def getSymbolLocation(symbol):
    return SymbolLocation(symbol.filename.name, 
                          symbol.start_line,
                          symbol.start_col,
                          symbol.end_line,
                          symbol.end_col,
                          symbol.symbolkind.name)

__all__ = [ 'IndexDB', 'IndexDBWriter', 'IndexDBReader', 'SymbolLocation' ]

if __name__ == "__main__":
#    storm.tracer.debug(True)
    dbName = "/data/work/clang-browser/src/python/symbols.db"
    dbw = IndexDBWriter(dbName)
    dbw.initialize(clang.cindex.CursorKind.get_all_kinds())
    filename = "/data/work/clang-browser/src/hw.c"
    defloc = SymbolLocation(filename, 3, 12, 3, 5, 
                            clang.cindex.CursorKind.VAR_DECL)
    refloc = SymbolLocation(filename, 4, 12, 4, 5, 
                      clang.cindex.CursorKind.DECL_REF_EXPR)
    dbw.insertDefinitionNode(defloc)
    dbw.stormdb.commit()  #Why do someneed to commit
    #what is the difference between commit and flush
    dbw.insertReferenceNode(refloc, defloc)
    dbw.stormdb.commit()
    del dbw

    refloc2 = SymbolLocation(filename, 4, 12, 4, 5, 
                             clang.cindex.CursorKind.DECL_REF_EXPR)
    dbr = IndexDBReader(dbName)
    cur = dbr.getDefinitionNode(refloc2)
    print "Definition Node %s for Reference Node %s" % (cur, refloc2)

    ref = dbr.getReferenceNodes(defloc)
    for r in ref:
        print "Reference (%s) " % r
        print getSymbolLocation(r)
        

if __name__ == '__main__2':
    print SymbolKind.createTableString()
    print FileName.createTableString()
    print Symbol.createTableString()

    db = create_database("sqlite:/home/manish/symboldb.db")
    store = Store(db)
    
    #Create SymbolKind Table and populate with Clang SymbolKinds
    store.execute(SymbolKind.createTableString())
    for kind in clang.cindex.SymbolKind.get_all_kinds():
        print kind
        ck = SymbolKind(kind.name, kind.value)
        store.add(ck)
        store.flush()
        print "%r %s %d" % (ck.id, ck.name, ck.value)

    ck = store.find(SymbolKind, SymbolKind.value == 500).one()
    print ck

    #Add hw.c as a dummy file
    store.execute(FileName.createTableString())
    fl = FileName(u"/data/work/clang-browser/src/hw.c")
    store.add(fl)
    store.flush()
    print fl

    filename = store.find(FileName, FileName.name == 
                          u"/data/work/clang-browser/src/hw.c").one()
    print filename.name

    #Create Symbol table and fill with some dummy data
    store.execute(Symbol.createTableString())
    c1 = Symbol(Location(filename.name, 3, 12, 3, 5), 1, 9)
    c2 = Symbol(Location(filename.name, 4, 12, 4, 5), 1, 9)
    store.add(c1)
    store.add(c2)
    store.flush()

    store.execute(DefinitionSymbol.createTableString())
    dc = DefinitionSymbol()
    dc.defsymbol = c1
    dc.references.add(c1)
    dc.references.add(c2)
    store.add(dc)
    store.flush()
    print "DC"
    print dc.defsymbol
    print dc.references.count()
    for r in dc.references:
        print r
    
    del dc
    dc = store.get(DefinitionSymbol, 1)
    print dc.defsymbol
    print dc.references.count()
    for r in dc.references:
        print r
    

    store.commit()
    del store
