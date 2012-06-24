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

def unhandledKind(kind):
    return kind in [CursorKind.USING_DECLARATION]

class Indexer:
    def __init__(self, DBName=DEFAULT_DBNAME):
        self.indexDB    = IndexDBWriter(os.path.abspath(DBName))
        self.indexDB.initialize(CursorKind.get_all_kinds())
        self.count =0

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
        
    def insertDefinitionNode(self, node):
        kind = node.kind
        if kind.is_invalid() or unexposedKind(kind) or \
                unhandledKind(kind) :
            return

        nodeLoc = self.createNode(node)
        if nodeLoc == None:
            return

        # sys.stderr.write("idn: kind: %s filename: %s sl: %d sc: %d el: %d ec: %d\n" %
        #                  (kind.name, nodeLoc.filename, nodeLoc.sl, 
        #                   nodeLoc.sc, nodeLoc.el, 
        #                   nodeLoc.ec))
        
        if node.is_definition() or ( \
            ( type(node.get_ref()) != types.NoneType) and \
                self.createNode(node.get_ref()) == nodeLoc ):
            self.indexDB.insertDefinitionNode(nodeLoc)
            self.indexDB.commit()
        return

    def insertReferenceNode(self, node):
        kind = node.kind
        if kind.is_invalid() or unexposedKind(kind) or \
                unhandledKind(kind) :
            return

        nodeLoc = self.createNode(node)
        if nodeLoc == None or node.is_definition():
            return

        if ( type(node.get_ref()) != types.NoneType ):
            refNodeLoc = self.createNode(node.get_ref())
            if refNodeLoc != None and refNodeLoc != nodeLoc :
                self.indexDB.insertReferenceNode(nodeLoc, refNodeLoc)
                if self.count%1000 == 0:  self.indexDB.commit() 
        return

    def insertNode(self, node, insertDefs):        
        kind = node.kind
        if kind.is_invalid() or unexposedKind(kind) or \
                unhandledKind(kind) :
            return

        nodeLoc = self.createNode(node)
        if nodeLoc == None:
            return

        # self.printNode(node)
        # print "nodeLoc: %s\n" % nodeLoc
        if node.is_definition() and insertDefs:
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

    def visitSubTreeDepthFirst(self, root):
        stack = [root]
        while len(stack) != 0:
            node = stack.pop()
            for c in node.get_children():
                stack.append(c)
            yield node

    def visitSubTreeBreadthFirst(self, root):
        queue = collections.deque([root])
        while len(queue) != 0:
            node = queue.popleft()
            for c in node.get_children():
                queue.append(c)
            yield node

    def printNode(self, node):
        print "node: { %s %s %s } " % (node.spelling, node.kind, node.location)

    def insertSubTree(self, nodeQ, insertDefs):
        self.count = 0
        while len(nodeQ) != 0:
            node = nodeQ.popleft()
            if insertDefs:
                self.insertDefinitionNode(node)
            else:
                self.insertReferenceNode(node)

            # filename = node.extent.start.file.name \
            #     if node.extent.start.file != None else "<node>"
            # sys.stderr.write("ist: kind: %s filename: %s sl: %d sc: %d el: %d ec: %d\n" %
            #                  (node.kind.name, filename, 
            #                   node.extent.start.line,
            #                   node.extent.start.column,
            #                   node.extent.end.line,
            #                   node.extent.end.column))

            self.count = self.count + 1
            if (self.count % 100) == 0 :
                sys.stderr.write(".")

            for c in node.get_children():
                nodeQ.append(c)

    def index(self, filename, compiler_opts=[]):
        index            = Index.create()
        fullpathFilename = os.path.abspath(filename)
        tu               = index.parse(fullpathFilename, compiler_opts)
        if not tu:
            sys.stderr.write("Error: in loading file %s\n" % fullpathFilename)
            return
        root = tu.cursor
        # for n in self.visitSubTreeBreadthFirst(root):
        #     self.insertNode(n)
        self.insertSubTree(collections.deque([root]), True)
        sys.stderr.write("Number of nodes: %d\n" % self.count)
        self.insertSubTree(collections.deque([root]), False)
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

    if not os.path.exists(args[0]):
        sys.stderr.write("Error: source file %s does not exist" % args[0])

    return (opts, args)

__all__ = ['Indexer']

def main():
    (opts, args) = optParser()
    print opts.dbName
    indexer = Indexer(opts.dbName)
    print args
    indexer.index(args[0], args[1:])

#Main entry point
if __name__ == '__main__':
    main()
