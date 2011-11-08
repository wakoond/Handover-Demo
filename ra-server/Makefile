TARGET=ra-server

SRCS:=main.c
HDRS:=
OBJS:=${SRCS:.c=.o}

CFLAGS:= -Wall -g
LDFLAGS:=-lpthread

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS) $(LDFLAGS)

$(OBJS): $(HDRS) Makefile

clean: 
	rm -rf $(OBJS) $(TARGET)
.PHONY:clean

