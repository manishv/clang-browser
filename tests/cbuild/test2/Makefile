
all: test.exe

test.exe: test1.c test2.c
	${CC} $? -o $@

clean:
	-rm -f test.exe test1.o test2.o