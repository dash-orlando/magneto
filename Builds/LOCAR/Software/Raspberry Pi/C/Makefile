CC = gcc
CFLAGS=-O3 -funroll-loops -Wall -march=native #-g #-ffast-math #-pg
LAPACKLIBS_PATH=/usr/local/lib
LDFLAGS=-L$(LAPACKLIBS_PATH) -L.
LAPACKLIBS=-llapack -lblas -lf2c
LIBS=$(LAPACKLIBS)

.PHONY: all
all: magneto

magneto: magneto.cpp
	$(CC) $(CFLAGS) -c -o magneto.o magneto.cpp
	$(CC) $(LDFLAGS) -Wall -O2 magneto.o -o magneto -llsm9ds1 -lwiringPi -llevmar $(LIBS) -lm

clean:
	rm -f magneto
