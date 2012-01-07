import collections
import sys

import clang.cindex
import storm.exceptions
from storm.locals import *
import storm.tracer

class CursorKind(object):
    __storm_table__ = "cursorkind"
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
        return "CREATE TABLE IF NOT EXISTS cursorkind "\
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

class Cursor(Storm):
    __storm_table__ = "cursor"
    filename_id   = Int()
    filename      = Reference(filename_id, FileName.id)
    cursorkind_id = Int()
    cursorkind    = Reference(cursorkind_id, CursorKind.id)
    start_line    = Int()
    start_col    = Int()
    end_line      = Int()
    end_col      = Int()
    definition_id = Int()
    definition = Reference(definition_id, "DefinitionCursor.id")
    id = Int(primary=True)
    
    def __init__(self, location, 
                 filename_id=None, cursorkind_id=None):
        self.start_line    = location.sl
        self.start_col     = location.sc
        self.end_line      = location.el
        self.end_col       = location.ec
        self.filename_id   = filename_id
        self.cursorkind_id = cursorkind_id

    def __str__(self):
        return "<id : %r kind: %s filename: %s [%d:%d - %d:%d] >" % \
            (self.id, self.cursorkind.name, self.filename.name, 
             self.start_line, self.start_col, 
             self.end_line, self.end_col)

    @staticmethod
    def createTableString():
        return "CREATE TABLE IF NOT EXISTS cursor "\
            "(id INTEGER PRIMARY KEY, "\
            "filename_id INTEGER, cursorkind_id INTEGER, "\
            "definition_id INTEGER, "\
            "start_line INTEGER, start_col INTEGER, "\
            "end_line INTEGER, end_col INTEGER)"

class DefinitionCursor(Storm):
    __storm_table__ = "defcursor"
    id = Int(primary=True)
    defcursor_id = Int()
    defcursor    = Reference(defcursor_id, Cursor.id)
    references   = ReferenceSet(id, Cursor.definition_id)

    def __init__(self):
        pass

    def __str__(self):
        refstr = [str(r) for r in self.references]
        string = "< " + str(self.defcursor) + "Refs: " + ",".join(refstr) + " >"
        return string

    @staticmethod
    def createTableString():
        return "CREATE TABLE IF NOT EXISTS defcursor "\
            "(id INTEGER PRIMARY KEY, defcursor_id INTEGER)"
                                 

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
        self.stormdb.execute(CursorKind.createTableString())
        self.stormdb.execute(FileName.createTableString())
        self.stormdb.execute(Cursor.createTableString())
        self.stormdb.execute(DefinitionCursor.createTableString())

        #Variable to cache the last filename
        self.lastfile = None        

    def initialize(self, cursorKinds):
        #Populate the data in CursorKind, if it is already not created
        try:
            results = self.stormdb.get(CursorKind, 1)
            if not results:
                for kind in cursorKinds:
                    self.stormdb.add(CursorKind(kind.name, kind.value))
                self.stormdb.commit()
        except storm.exceptions.StormError:
            self.stormdb.rollback()
            sys.stderr.write("Error: writing to the database (%s)\n" % 
                             self.dbname)
            sys.exit(1)
        return self

    def getFileName(self, name):
        unicodeName = unicode(name)
        result  = self.stormdb.find(FileName, FileName.name == unicodeName)
        newfile = None
        if not result.is_empty():
            assert (result.count()==1)
            newfile = result.one()
        return newfile
            
    def getNodeKind(self, nodeKind):
        result = self.stormdb.find(CursorKind, CursorKind.value == 
                                   nodeKind.value)
        assert (not result.is_empty())
        return result.one()

    def getCursor(self, location):
        results = self.stormdb.get(FileName, 1)
        print "results: ", results
        fileId = self.getFileName(location.filename).id
        print location
        result = self.stormdb.find(Cursor, 
                                    Cursor.filename_id == fileId,
                                    Cursor.start_line  == location.sl,
                                    Cursor.start_col   == location.sc,
                                    Cursor.end_line    == location.el,
                                    Cursor.end_col     == location.ec)
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

        if self.getCursor(location) == None :
            cursor = Cursor(location, fileId, nodeKindId)
            self.stormdb.add(cursor)
            self.stormdb.flush()
            defCursor = DefinitionCursor()
            defCursor.defcursor = cursor
            defCursor.references.add(cursor)
            self.stormdb.flush()
            print "Cursor.Definition %s " % cursor.definition
        else:
            print "Cursor already present"

    #TODO: Need to implement rollback and errorhandling
    def insertReferenceNode(self, location, defLocation):
        fileId     = self.getOrInsertFileName(location.filename).id
        nodeKindId = self.getNodeKind(location.nodekind).id
        assert (fileId != None and nodeKindId != None)
        
        if self.getCursor(location) == None:
            cursor = Cursor(location, fileId, nodeKindId)
            self.stormdb.add(cursor)
            self.stormdb.flush()
            defCursor = self.getCursor(defLocation).definition
            defCursor.references.add(cursor)
            self.stormdb.flush()
            print "Cursor.Definition %s " % defCursor
        else:
            print "Reference Cursor is already present"

class IndexDBReader(IndexDB):
        
    def getDefinitionNode(self, refLocation):
        print refLocation
        refCursor = self.getCursor(refLocation)
        defCursor = refCursor.definition
        return defCursor

    def getReferenceNodes(self, defloc):
        pass
    

__all__ = [ 'IndexDB', 'IndexDBWriter', 'IndexDBReader', 'SymbolLocation' ]

if __name__ == "__main__":
#    storm.tracer.debug(True)
    dbw = IndexDBWriter("/data/work/clang-browser/src/python/symbols.db")
    dbw.initialize(clang.cindex.CursorKind.get_all_kinds())
    filename = "/data/work/clang-browser/src/hw.c"
    defloc = SymbolLocation(filename, 3, 12, 3, 5, 
                            clang.cindex.CursorKind.VAR_DECL)
    refloc = SymbolLocation(filename, 4, 12, 4, 5, 
                      clang.cindex.CursorKind.DECL_REF_EXPR)
    dbw.insertDefinitionNode(defloc)
    dbw.stormdb.commit()
    dbw.insertReferenceNode(refloc, defloc)
    dbw.stormdb.commit()
    del dbw

    dbr = IndexDBReader("/home/manish/symbols.db")
    cur = dbr.getDefinitionNode(refloc)
    print "Definition Node %s for Reference Node %s" % (cur, refloc)


if __name__ == '__main__2':
    print CursorKind.createTableString()
    print FileName.createTableString()
    print Cursor.createTableString()

    db = create_database("sqlite:/home/manish/symboldb.db")
    store = Store(db)
    
    #Create CursorKind Table and populate with Clang CursorKinds
    store.execute(CursorKind.createTableString())
    for kind in clang.cindex.CursorKind.get_all_kinds():
        print kind
        ck = CursorKind(kind.name, kind.value)
        store.add(ck)
        store.flush()
        print "%r %s %d" % (ck.id, ck.name, ck.value)

    ck = store.find(CursorKind, CursorKind.value == 500).one()
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

    #Create Cursor table and fill with some dummy data
    store.execute(Cursor.createTableString())
    c1 = Cursor(Location(filename.name, 3, 12, 3, 5), 1, 9)
    c2 = Cursor(Location(filename.name, 4, 12, 4, 5), 1, 9)
    store.add(c1)
    store.add(c2)
    store.flush()

    store.execute(DefinitionCursor.createTableString())
    dc = DefinitionCursor()
    dc.defcursor = c1
    dc.references.add(c1)
    dc.references.add(c2)
    store.add(dc)
    store.flush()
    print "DC"
    print dc.defcursor
    print dc.references.count()
    for r in dc.references:
        print r
    
    del dc
    dc = store.get(DefinitionCursor, 1)
    print dc.defcursor
    print dc.references.count()
    for r in dc.references:
        print r
    

    store.commit()
    del store
