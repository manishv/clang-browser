
all: test.exe

%.o: %.c
	${CC} -c $< -o $@

test.exe: test.o test2.o
	${CC} $? -o $@

clean:
	-rm -f *.o test.exe