#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include <stdarg.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <signal.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <pthread.h>

#define BUF_SIZE        512
#define PID_BUF_SIZE    512
#define ERR_BUF_SIZE    512

static int port_num = 0;
static char * radvd_path = NULL;
static char * radvd_an1_pidfile = NULL;
static char * radvd_an2_pidfile = NULL;
static char ** an1_args = NULL;
static int an1_args_num = 0;
static pid_t an1_pid = 0;
static char ** an2_args = NULL;
static int an2_args_num = 0;
static pid_t an2_pid = 0;
static pthread_mutex_t pid_lock = PTHREAD_MUTEX_INITIALIZER;


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
#define OPTS_STATE_AN1      1
#define OPTS_STATE_AN2      2
    
    an1_args_num++;
    an1_args = realloc(an1_args, sizeof(char *) * an1_args_num);
    if (an1_args == NULL) {
        error(-1, "Unable to allocate args");
        exit(1);
    }
    an1_args[an1_args_num-1] = strdup("radvd");

    an2_args_num++;
    an2_args = realloc(an2_args, sizeof(char *) * an2_args_num);
    if (an2_args == NULL) {
        error(-1, "Unable to allocate args");
        exit(1);
    }
    an2_args[an2_args_num-1] = strdup("radvd");

    for (i = 1; i < argc; i++) {
        switch (state) {
        case OPTS_STATE_MAIN:
            if (strcmp(argv[i], "-P") == 0) {
                i++;
                port_num = strtoul(argv[i], NULL, 10);
            } else if (strcmp(argv[i], "--radvd-path") == 0) {
                i++;
                if (radvd_path != NULL)
                    free(radvd_path);
                radvd_path = strdup(argv[i]);
            } else if (strcmp(argv[i], "--radvd-an1-pidfile") == 0) {
                i++;
                if (radvd_an1_pidfile != NULL)
                    free(radvd_an1_pidfile);
                radvd_an1_pidfile = strdup(argv[i]);
            } else if (strcmp(argv[i], "--radvd-an2-pidfile") == 0) {
                i++;
                if (radvd_an2_pidfile != NULL)
                    free(radvd_an2_pidfile);
                radvd_an2_pidfile = strdup(argv[i]);
            } else if (strcmp(argv[i], "--an1") == 0) {
                state = OPTS_STATE_AN1;
            } else if (strcmp(argv[i], "--an2") == 0) {
                state = OPTS_STATE_AN2;
            }
            break;
        case OPTS_STATE_AN1:
            if (strcmp(argv[i], "--an2") == 0) {
                state = OPTS_STATE_AN2;
                break;
            }
            an1_args_num++;
            an1_args = realloc(an1_args, sizeof(char *) * an1_args_num);
            if (an1_args == NULL) {
                error(-1, "Unable to allocate args");
                exit(1);
            }
            an1_args[an1_args_num-1] = strdup(argv[i]);
            if (an1_args[an1_args_num-1] == NULL) {
                error(-1, "Unable to duplicate arg %d", an1_args_num);
                exit(1);
            }
            break;
        case OPTS_STATE_AN2:
            if (strcmp(argv[i], "--an1") == 0) {
                state = OPTS_STATE_AN1;
                break;
            }
            an2_args_num++;
            an2_args = realloc(an2_args, sizeof(char *) * an2_args_num);
            if (an2_args == NULL) {
                error(-1, "Unable to allocate args");
                exit(1);
            }
            an2_args[an2_args_num-1] = strdup(argv[i]);
            if (an2_args[an2_args_num-1] == NULL) {
                error(-1, "Unable to duplicate arg %d", an2_args_num);
                exit(1);
            }
            break;
        }
    }

    if (port_num == 0) {
        error(-1, "You must specify a port number");
        exit(1);
    }

    if (radvd_path == NULL || access(radvd_path, R_OK | X_OK) != 0) {
        error(-1, "You must specify a valid radvd path");
        exit(1);
    }

    if (radvd_an1_pidfile == NULL || radvd_an2_pidfile == NULL) {
        error(-1, "You must specify radvd pidfile path for both ANs");
        exit(1);
    }

    free(an1_args[0]);
    free(an2_args[0]);
    an1_args[0] = strdup(radvd_path);
    an2_args[0] = strdup(radvd_path);

    debug("AN1 radvd options:");
    for (i = 0; i < an1_args_num; i++) 
        debug("  #%02d# %s", i+1, an1_args[i]);
    debug("AN2 radvd options:");
    for (i = 0; i < an2_args_num; i++) 
        debug("  #%02d# %s", i+1, an2_args[i]);
	
    an1_args_num++;
    an1_args = realloc(an1_args, sizeof(char *) * an1_args_num);
    if (an1_args == NULL) {
        error(-1, "Unable to allocate args");
        exit(1);
    }
    an1_args[an1_args_num-1] = NULL;
	
    an2_args_num++;
    an2_args = realloc(an2_args, sizeof(char *) * an2_args_num);
    if (an2_args == NULL) {
        error(-1, "Unable to allocate args");
        exit(1);
    }
    an2_args[an2_args_num-1] = NULL;

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
        pthread_mutex_lock(&pid_lock);
        *ra_pid = pid;
        pthread_mutex_unlock(&pid_lock);
        return;
    }

    ret = execv(radvd_path, args);
    error(ret, "Unable to start radvd, execv error");
}

void stop_radvd(pid_t * ra_pid)
{
    int ret;
    pid_t pid;
        
    pthread_mutex_lock(&pid_lock);
    pid = *ra_pid;
    pthread_mutex_unlock(&pid_lock);

    ret = kill(*ra_pid, SIGINT);
    if (ret)
        error(ret, "Unable to send SIGINT to %d", (int)*ra_pid);
    else {
        pthread_mutex_lock(&pid_lock);
        *ra_pid = 0;
        pthread_mutex_unlock(&pid_lock);
    }
}

void * wait_thread(void * arg)
{
    pid_t pid;
    int status;
    int ret;
    int fd;
    char buffer[PID_BUF_SIZE];
    pid_t pid_buf, pid_chk;

    for(;;) {
        pid = wait(&status);
        if (pid < 0) {
            if (errno == ECHILD) 
                sleep(1);
            else {
                error(pid, "Wait error");
                exit(1);
            }
        } else
            debug("Child process (radvd) exites with status: %d [PID %d]", status, pid);

        ret = open(radvd_an1_pidfile, O_RDONLY);
        if (ret <= 0) {
            pthread_mutex_lock(&pid_lock);
            pid_chk = an1_pid;
            pthread_mutex_unlock(&pid_lock);
            if (pid_chk > 0) {
                debug("AN1 radvd unexpectedly quit");
                pthread_mutex_lock(&pid_lock);
                an1_pid = 0;
                pthread_mutex_unlock(&pid_lock);
            }
        } else {
            fd = ret;
            ret = read(fd, buffer, sizeof(buffer));
            close(fd);
            if (ret <= 0) {
                error(ret, "Unable to read from pidfile: %s", radvd_an1_pidfile);
                exit(1);
            }
            buffer[ret] = '\0';
            pid_buf = strtoul(buffer, NULL, 10);
            pthread_mutex_lock(&pid_lock);
            pid_chk = an1_pid;
            pthread_mutex_unlock(&pid_lock);
            if (pid_chk != pid_buf) {
                debug("AN1 radvd pid changed from %d to %d", pid_chk, pid_buf);
                pthread_mutex_lock(&pid_lock);
                an1_pid = pid_buf;
                pthread_mutex_unlock(&pid_lock);
            }
        }

        ret = open(radvd_an2_pidfile, O_RDONLY);
        if (ret <= 0) {
            pthread_mutex_lock(&pid_lock);
            pid_chk = an2_pid;
            pthread_mutex_unlock(&pid_lock);
            if (pid_chk > 0) {
                debug("AN2 radvd unexpectedly quit");
                pthread_mutex_lock(&pid_lock);
                an2_pid = 0;
                pthread_mutex_unlock(&pid_lock);
            }
        } else {
            fd = ret;
            ret = read(fd, buffer, sizeof(buffer));
            close(fd);
            if (ret <= 0) {
                error(ret, "Unable to read from pidfile: %s", radvd_an2_pidfile);
                exit(1);
            }
            buffer[ret] = '\0';
            pid_buf = strtoul(buffer, NULL, 10);
            pthread_mutex_lock(&pid_lock);
            pid_chk = an2_pid;
            pthread_mutex_unlock(&pid_lock);
            if (pid_chk != pid_buf) {
                debug("AN2 radvd pid changed from %d to %d", pid_chk, pid_buf);
                pthread_mutex_lock(&pid_lock);
                an2_pid = pid_buf;
                pthread_mutex_unlock(&pid_lock);
            }
        }
    }

    return NULL;
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

#define SEL_AN1     1
#define SEL_AN2     2

    for (blen = read(fd, buffer, sizeof(buffer) - 1); blen > 0 && blen < sizeof(buffer); blen = read(fd, buffer, sizeof(buffer) - 1)) {
        buffer[blen] = '\0';
	    debug("Incoming raw command: %s", buffer);
        command = 0;
        selector = 0;
        p = buffer;
        for (i = 0; i < blen; i++) {
            if (buffer[i] == '|' || buffer[i] == '\n') {
                buffer[i] = '\0';
                if (strcmp(p, "START") == 0)
                    command = CMD_START;
                else if (strcmp(p, "STOP") == 0)
                    command = CMD_STOP;
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
            if (strcmp(p, "radvd-an1") == 0)
                selector = SEL_AN1;
            else if (strcmp(p, "radvd-an2") == 0)
                selector = SEL_AN2;
        }
    
        if (command == 0 || (selector == 0 && command != CMD_GET)) {
            error(-1, "Invalid command: c %d s %d", command, selector);
            continue;
        }

        debug("Incoming command: %s %s", (command == CMD_START) ? "/start/" : (command == CMD_STOP) ? "/stop/" : "/get/", 
                (selector == SEL_AN1) ? "/AN1/" : (selector == SEL_AN2) ? "/AN2/" : "//");

        switch(command) {
        case CMD_START:
            switch(selector) {
            case SEL_AN1:
                start_radvd(an1_args, &an1_pid);
                break;
            case SEL_AN2:
                start_radvd(an2_args, &an2_pid);
                break;
            }
            break;
        case CMD_STOP:
            switch(selector) {
            case SEL_AN1:
                stop_radvd(&an1_pid);
                break;
            case SEL_AN2:
                stop_radvd(&an2_pid);
                break;
            }
            break;
        case CMD_GET:
            break;
        }
            
        memset(buffer, 0, sizeof(buffer));
        snprintf(buffer, sizeof(buffer), "STATUS|radvd-an1|%s|radvd-an2|%s", 
                (an1_pid == 0) ? "stopped" : "running",
                (an2_pid == 0) ? "stopped" : "running");
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

    ret = pthread_create(&th, &thattr, wait_thread, NULL);
    if (ret < 0) {
        error(ret, "Unable to create thread");
        exit(1);
    }

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

