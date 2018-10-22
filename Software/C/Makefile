CC = gcc
.PHONY: all
all: magneto

magneto: magneto.cpp
	$(CC) -Wall -O2 magneto.cpp -o magneto -llsm9ds1 -lwiringPi

clean:
	rm -f magneto
