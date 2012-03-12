// RUN: python indexdb_test1.py %s | FileCheck %s

// CHECK: Definition Node  < <id : 1 kind: VAR_DECL filename: /data/work/clang-browser/src/hw.c [3:5 - 3:12] >Refs: <id : 1 kind: VAR_DECL filename: /data/work/clang-browser/src/hw.c [3:5 - 3:12] >,<id : 2 kind: DECL_REF_EXPR filename: /data/work/clang-browser/src/hw.c [4:5 - 4:12] >,<id : 3 kind: DECL_REF_EXPR filename: /data/work/clang-browser/src/hw.c [5:5 - 5:12] >,<id : 4 kind: DECL_REF_EXPR filename: /data/work/clang-browser/src/hw.c [6:5 - 6:12] > >
// CHECK: Reference Node < filename: /data/work/clang-browser/src/hw.c sl: 4 sc: 5 el: 4 ec: 12 nodekind: CursorKind.DECL_REF_EXPR >
// CHECK: Cur1 == Cur2  True
