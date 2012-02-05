// RUN: python indexdb_test2.py %s | FileCheck %s

// CHECK: Definition Node  < <id : 1 kind: VAR_DECL filename: /data/work/clang-browser/src/hw.c [3:5 - 3:12] >Refs: <id : 1 kind: VAR_DECL filename: /data/work/clang-browser/src/hw.c [3:5 - 3:12] >,<id : 2 kind: DECL_REF_EXPR filename: /data/work/clang-browser/src/hw.c [4:5 - 4:12] >,<id : 3 kind: DECL_REF_EXPR filename: /data/work/clang-browser/src/hw.c [5:5 - 5:12] >,<id : 4 kind: DECL_REF_EXPR filename: /data/work/clang-browser/src/hw.c [6:5 - 6:12] > >
