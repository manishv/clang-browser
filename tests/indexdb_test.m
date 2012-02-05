// RUN: python indexdb_test.py %s | FileCheck %s

// CHECK: Definition Node < <id : 1 kind: VAR_DECL filename: /data/work/clang-browser/src/hw.c [3:12 - 3:5] >Refs: <id : 1 kind: VAR_DECL filename: /data/work/clang-browser/src/hw.c [3:12 - 3:5] >,<id : 2 kind: DECL_REF_EXPR filename: /data/work/clang-browser/src/hw.c [4:12 - 4:5] > > for Reference Node SymbolLocation(filename='/data/work/clang-browser/src/hw.c', sl=4, sc=12, el=4, ec=5, nodekind=CursorKind.DECL_REF_EXPR)
