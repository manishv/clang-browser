import sys, os, types, collections
from optparse import OptionParser
from indexdb import *
from clang.cindex import *

DEFAULT_DBNAME="symbols.db"

def unexposedKind(kind):
    return kind == CursorKind.UNEXPOSED_DECL or \
        kind == CursorKind.UNEXPOSED_EXPR or \
        kind == CursorKind.UNEXPOSED_STMT or \
        kind == CursorKind.UNEXPOSED_ATTR

class Indexer:
    def __init__(self, DBName=DEFAULT_DBNAME):
        self.indexDB    = IndexDBWriter(os.path.abspath(DBName))
        self.indexDB.initialize(CursorKind.get_all_kinds())


    def __del__(self):
        del self.indexDB

    def createNode(self, node):
        assert isinstance(node, Cursor)
        kind     = node.kind
        extent   = node.extent
        filename = extent.start.file.name \
            if extent.start.file != None else None

        if filename == None:
            return None

        sl = extent.start.line
        sc = extent.start.column
        el = extent.end.line
        ec = extent.end.column

        return SymbolLocation(filename, sl, sc, el, ec, kind)
        

    def insertNode(self, node):        
        kind = node.kind
        if kind.is_invalid() or unexposedKind(kind):
            return

        nodeLoc = self.createNode(node)
        if nodeLoc == None:
            return

        if node.is_definition():
            self.indexDB.insertDefinitionNode(nodeLoc)
            self.indexDB.commit()
        #TODO: Can we update the following statement with isNull()
        elif type(node.get_ref()) != types.NoneType: 
            defNodeLoc = self.createNode(node.get_ref())
            assert (defNodeLoc!=None)
            if nodeLoc == defNodeLoc:
                self.indexDB.insertDefinitionNode(nodeLoc)
            else:
                self.indexDB.insertReferenceNode(nodeLoc,defNodeLoc)
            self.indexDB.commit()
        return

    def printNode(self, node):
        print "node: { %s %s %s } " % (node.spelling, node.kind, node.location)

    def insertSubTree(self, nodeQ):
        if len(nodeQ) == 0:
            return;
        node = nodeQ.popleft()
        self.insertNode(node)
        for c in node.get_children():
            nodeQ.append(c)
        self.insertSubTree(nodeQ)

    def index(self, filename, compiler_opts=[]):
        index            = Index.create()
        fullpathFilename = os.path.abspath(filename)
        tu               = index.parse(fullpathFilename, compiler_opts)
        if not tu:
            sys.stderr.write("Error: in loading file %s\n" % fullpathFilename)
            return
        root = tu.cursor
        self.insertSubTree(collections.deque([root]))
        return


def optParser():
    parser = OptionParser(
        "Usage: %prog [options] {filename} [compiler-opts*]")

    parser.add_option("", "--db", dest="dbName", default=DEFAULT_DBNAME,
                      help="Name of index database (default: %s)" % 
                      DEFAULT_DBNAME)

    parser.disable_interspersed_args()
    (opts, args) = parser.parse_args()
    if len(args) == 0:
        parser.error('Invalid number of arguments')

    return (opts, args)

def main():
    (opts, args) = optParser()
    print opts.dbName
    indexer = Indexer(opts.dbName)
    print args
    indexer.index(args[0], args[1:])

#Main entry point
if __name__ == '__main__':
    main()
