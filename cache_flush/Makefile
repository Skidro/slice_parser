CC=gcc
CXX=g++
PGMS=cache_flush

CFLAGS=-O0 -static
CXXFLAGS=$(CFLAGS)
LDFLAGS=-Wl,--no-as-needed -lrt -static

all: $(PGMS)

cache_flush: cache_flush.o

clean:
	rm -f *.o *~ $(PGMS)
