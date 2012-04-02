// RUN: cbrowse --help | FileCheck %s

// CHECK: Usage: cbrowse [options] <cmd> <cmd_args> 
// CHECK: available commands are: 
// CHECK:   build: builds the index database 
// CHECK:   find-def: find the definition 
// CHECK:   find-ref: find all references to the symbol 


//CHECK: Options:
//CHECK:  -h, --help         show this help message and exit
//CHECK:  --dbname=DATABASE  Name of index database (default: symbols.db)

