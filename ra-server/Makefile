TARGET=ra-server

SRCS:=main.c
HDRS:=
OBJS:=${SRCS:.c=.o}

CFLAGS:= -Wall -g
LDFLAGS:=-lpthread

INSTALL_DIR:=/usr/sbin

all: $(TARGET)

install: $(TARGET)
	mkdir -p $(INSTALL_DIR)
	cp $(TARGET) $(INSTALL_DIR)

uninstall:
	[ ! -f $(INSTALL_DIR)/$(TARGET) ] || rm -rf $(INSTALL_DIR)/$(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS) $(LDFLAGS)

$(OBJS): $(HDRS) Makefile

clean: 
	rm -rf $(OBJS) $(TARGET)
.PHONY:clean

