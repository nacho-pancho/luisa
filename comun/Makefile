OBJ=pbm.o
CFLAGS=-O0 -g -Wall
LFLAGS=-lm

all: template

template: template.c $(OBJ)
	$(CC) $(LFLAGS) $(CFLAGS) $< $(OBJ) -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean: 
	rm -f *.o template
