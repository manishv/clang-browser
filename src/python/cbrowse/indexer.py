from optparse import OptionParser

DEFAULT_DBNAME="symbols.db"
class Indexer:
    def __init__(self, DBName=DEFAULT_DBNAME):
        self.DBAbsPath = os.path.abspath(DBName)
        self.SymbolsDB = SymbolsDB(self.DBAbsPath)

    def __del__(self):
        del self.SymbolsDB

    def index(self, filename, compiler_opts):
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
    indexer = Indexer()

#Main entry point
if __name__ == '__main__':
    main()
