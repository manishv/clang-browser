#include<stdio.h>
int foo(int i);
int foo(int i)
{
    return i+10;
}
int main() {
    int i=0;
    i=foo(i);
    printf("HW\n");
    return i;
}
