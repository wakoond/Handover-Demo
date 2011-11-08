#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include <stdarg.h>
#include <errno.h>
#include <sys/types.h>
#include <signal.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <pthread.h>

#define BUF_SIZE        512
#define ERR_BUF_SIZE    512

static int port_num = 0;
static char ** ar1_args = NULL;
static int ar1_args_num = 0;
static pid_t ar1_pid = 0;
static char ** ar2_args = NULL;
static int ar2_args_num = 0;
static int ar2_pid = 0;


inline void error(int retval, char * fmt, ...)
{
    va_list vl;
    char err_fmt[ERR_BUF_SIZE];

    snprintf(err_fmt, sizeof(err_fmt), "[ERROR] %s\n", fmt);

    va_start(vl, fmt);
    vfprintf(stderr, err_fmt, vl);
    va_end(vl);
    fprintf(stderr, "[ERROR] [retval: %d] [error: %d %s]\n", retval, errno, strerror(errno));
}

inline void debug(char * fmt, ...)
{
    va_list vl;
    char dbg_fmt[ERR_BUF_SIZE];

    snprintf(dbg_fmt, sizeof(dbg_fmt), "[ DBG ] %s\n", fmt);

    va_start(vl, fmt);
    vfprintf(stdout, dbg_fmt, vl);
    va_end(vl);
}

void get_opts(int argc, char * argv[])
{
    int i;
    int state = 0;

#define OPTS_STATE_MAIN     0
#define OPTS_STATE_AR1      1
#define OPTS_STATE_AR2      2
    
    ar1_args_num++;
    ar1_args = realloc(ar1_args, sizeof(char *) * ar1_args_num);
    if (ar1_args == NULL) {
        error(-1, "Unable to allocate args");
        exit(1);
    }
    ar1_args[ar1_args_num-1] = "radvd";

    ar2_args_num++;
    ar2_args = realloc(ar2_args, sizeof(char *) * ar2_args_num);
    if (ar2_args == NULL) {
        error(-1, "Unable to allocate args");
        exit(1);
    }
    ar2_args[ar2_args_num-1] = "radvd";

    for (i = 1; i < argc; i++) {
        switch (state) {
        case OPTS_STATE_MAIN:
            if (strcmp(argv[i], "-P") == 0) {
                i++;
                port_num = strtoul(argv[i], NULL, 10);
            } else if (strcmp(argv[i], "--ar1") == 0) {
                state = OPTS_STATE_AR1;
            } else if (strcmp(argv[i], "--ar2") == 0) {
                state = OPTS_STATE_AR2;
            }
            break;
        case OPTS_STATE_AR1:
            if (strcmp(argv[i], "--ar2") == 0) {
                state = OPTS_STATE_AR2;
                break;
            }
            ar1_args_num++;
            ar1_args = realloc(ar1_args, sizeof(char *) * ar1_args_num);
            if (ar1_args == NULL) {
                error(-1, "Unable to allocate args");
                exit(1);
            }
            ar1_args[ar1_args_num-1] = strdup(argv[i]);
            if (ar1_args[ar1_args_num-1] == NULL) {
                error(-1, "Unable to duplicate arg %d", ar1_args_num);
                exit(1);
            }
            break;
        case OPTS_STATE_AR2:
            if (strcmp(argv[i], "--ar1") == 0) {
                state = OPTS_STATE_AR1;
                break;
            }
            ar2_args_num++;
            ar2_args = realloc(ar2_args, sizeof(char *) * ar2_args_num);
            if (ar2_args == NULL) {
                error(-1, "Unable to allocate args");
                exit(1);
            }
            ar2_args[ar2_args_num-1] = strdup(argv[i]);
            if (ar2_args[ar2_args_num-1] == NULL) {
                error(-1, "Unable to duplicate arg %d", ar2_args_num);
                exit(1);
            }
            break;
        }
    }

    if (port_num == 0) {
        error(-1, "You must specify a port number");
        exit(1);
    }

    debug("AR1 radvd options:");
    for (i = 0; i < ar1_args_num; i++) 
        debug("  #%02d# %s", i+1, ar1_args[i]);
    debug("AR2 radvd options:");
    for (i = 0; i < ar2_args_num; i++) 
        debug("  #%02d# %s", i+1, ar2_args[i]);
}

void start_radvd(char ** args, pid_t * ra_pid)
{
    pid_t pid;
    int ret;
    
    pid = fork();

    if (pid < 0) {
        error((int)pid, "Unable to fork radvd");
        exit(-1);
    }

    if (pid > 0) {
        debug("Radvd forked PID %d", (int)pid);
        *ra_pid = pid;
        return;
    }

    ret = execv("radvd", args);
}

void stop_radvd(pid_t * ra_pid)
{
    int ret;

    ret = kill(*ra_pid, SIGINT);
    if (ret)
        error(ret, "Unable to send SIGINT to %d", (int)*ra_pid);
    else
        *ra_pid = 0;
}

void * cli_thread(void * arg)
{
    int fd = (int)arg;
    char buffer[BUF_SIZE];
    size_t blen;
    int i;
    char * p;
    int command = 0;
    int selector = 0;

#define CMD_START   1
#define CMD_STOP    2
#define CMD_GET     3

#define SEL_AR1     1
#define SEL_AR2     2

    for (blen = read(fd, buffer, sizeof(buffer) - 1); blen > 0 && blen < sizeof(buffer); blen = read(fd, buffer, sizeof(buffer) - 1)) {
        buffer[blen] = '\0';
        command = 0;
        selector = 0;
        p = buffer;
        for (i = 0; i < blen; i++) {
            if (buffer[i] == '|' || buffer[i] == '\n') {
                buffer[i] = '\0';
                if (strcmp(p, "START") == 0)
                    command = CMD_START;
                else if (strcmp(p, "STOP") == 0)
                    command = CMD_GET;
                else if (strcmp(p, "GET") == 0)
                    command = CMD_GET;
                break;
            }
        }
        if (i < blen - 1) {
            p = &buffer[i+1];
            for (i = 0; i < blen; i++) {
                if (buffer[i] == '|' || buffer[i] == '\n') {
                    buffer[i] = '\0';
                }
            }
            if (strcmp(p, "radvd-ar1") == 0)
                selector = SEL_AR1;
            else if (strcmp(p, "radvd-ar2") == 0)
                selector = SEL_AR2;
        }
    
        if (command == 0 || (selector == 0 && command != CMD_GET)) {
            error(-1, "Invalid command");
            continue;
        }

        debug("Incoming command: %s %s", (command == CMD_START) ? "/start/" : (command == CMD_STOP) ? "/stop/" : "/get/", 
                (selector == SEL_AR1) ? "/ar1/" : (selector == SEL_AR2) ? "/ar2/" : "//");

        switch(command) {
        case CMD_START:
            switch(selector) {
            case SEL_AR1:
                start_radvd(ar1_args, &ar1_pid);
                break;
            case SEL_AR2:
                start_radvd(ar2_args, &ar2_pid);
                break;
            }
            break;
        case CMD_STOP:
            switch(selector) {
            case SEL_AR1:
                stop_radvd(&ar1_pid);
                break;
            case SEL_AR2:
                stop_radvd(&ar2_pid);
                break;
            }

            break;
        case CMD_GET:
            break;
        }
            
        memset(buffer, 0, sizeof(buffer));
        snprintf(buffer, sizeof(buffer), "STATUS|radvd-ar1|%s|radvd-ar2|%s", 
                (ar1_pid == 0) ? "stopped" : "running",
                (ar2_pid != 0) ? "stopped" : "running");
        debug("Status after command: %s", buffer);
        write(fd, buffer, strlen(buffer));
    }

    if (blen == 0)
        debug("Connection closed");
    else
        error(blen, "Connection error (read)");

    return NULL;
}

int main (int argc, char * argv[])
{
    int ret;
    int fd, cli;
    struct sockaddr_in addr;
    size_t addrlen;
    char addrbuf[50];
    const char * p;
    pthread_attr_t thattr;
    pthread_t th;

    get_opts(argc, argv);

    ret = socket(AF_INET, SOCK_STREAM, 0);
    if (ret <= 0) {
        error(ret, "Unable to open socket");
        exit(1);
    }
    fd = ret;

    addrlen = sizeof(addr);
    memset(&addr, 0, addrlen);
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port_num);
    ret = bind(fd, (struct sockaddr *) &addr, addrlen);
    if (ret < 0) {
        error(ret, "Unable to bind on port %d", port_num);
        exit(1);
    }
    listen(fd,5);

    pthread_attr_init(&thattr);
    pthread_attr_setdetachstate(&thattr, PTHREAD_CREATE_DETACHED);

    debug("Waiting for incoming connections on port %d...", port_num);
    for (;;) {
        addrlen = sizeof(addr);
        memset(&addr, 0, addrlen);
        ret = accept(fd, (struct sockaddr *) &addr, &addrlen);
        if (ret < 0) {
            error(ret, "Unable to accept incoming connection");
            exit(1);
        }
        cli = ret;
        memset(addrbuf, 0, sizeof(addrbuf));
        p = inet_ntop(AF_INET, &addr.sin_addr, addrbuf, sizeof(addrbuf));
        if (p == addrbuf) {
            debug("Accepted connection form %s:%d", addrbuf, ntohs(addr.sin_port));
        }

        ret = pthread_create(&th, &thattr, cli_thread, (void *)cli);
        if (ret < 0) {
            error(ret, "Unable to create thread");
            exit(1);
        }
    }

    return 0;
}

