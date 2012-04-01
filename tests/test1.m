// RUN: rm -f Output/test1.db
// RUN: cbrowse --dbname Output/test1.db build /data/work/clang-browser/tests/test1.c
// RUN: cbrowse --dbname Output/test1.db find-def /data/work/clang-browser/tests/test1.c 6 12 6 18 | FileCheck %s

// CHECK: Definition Node: < <id : 1 kind: FUNCTION_DECL filename: /data/work/clang-browser/tests/test1.c [1:1 - 3:2] >Refs: <id : 1 kind: FUNCTION_DECL filename: /data/work/clang-browser/tests/test1.c [1:1 - 3:2] >,<id : 6 kind: CALL_EXPR filename: /data/work/clang-browser/tests/test1.c [6:12 - 6:18] >,<id : 7 kind: CALL_EXPR filename: /data/work/clang-browser/tests/test1.c [6:21 - 6:29] >,<id : 8 kind: DECL_REF_EXPR filename: /data/work/clang-browser/tests/test1.c [6:12 - 6:15] >,<id : 10 kind: DECL_REF_EXPR filename: /data/work/clang-browser/tests/test1.c [6:21 - 6:24] > >

