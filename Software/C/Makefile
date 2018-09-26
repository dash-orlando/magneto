CC = gcc
.PHONY: all
all: magneto

magneto: magneto.cpp
	$(CC) -Wall -O2 magneto.cpp -o magneto -llsm9ds1 -lwiringPi
	
blink_test: blink_test.cpp
	$(CC) -Wall -O2 blink_test.cpp -o blink_test -lwiringPi

clean:
	rm -f magneto
	rm -f blink_test
