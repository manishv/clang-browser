int foo(int x) {
  return x;
}

int bar(int x) {
    return foo(x) + foo(x+1);
}
