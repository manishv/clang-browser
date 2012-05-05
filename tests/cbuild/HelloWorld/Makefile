
all: hw.exe

%.o: %c
	${CC} -c $< -o $@

hw.exe: hw.o
	${CC} $? -o $@

clean:
	-rm -f *.o *.db hw.exe 