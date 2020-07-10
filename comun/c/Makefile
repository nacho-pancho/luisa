OBJ=pbm.o
CFLAGS=-Wall
LFLAGS=-lm

all: template performance

template: template.c $(OBJ)
	$(CC) $(LFLAGS) $(CFLAGS) $< $(OBJ) -o $@

performance: performance.c
	#$(CC) $(CFLAGS) -fopenmp -march=sandybridge $< -o $@
	$(CC) $(CFLAGS) -fopenmp -march=ivybridge $< -o $@
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean: 
	rm -f *.o template performance
