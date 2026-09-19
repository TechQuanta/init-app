#include <stdio.h>
#include <stdlib.h>
#include "actions.h"
#include "../utils.h"

#ifdef _WIN32
    #include <direct.h>
    #define GETCWD _getcwd
    #define MKDIR(path) _mkdir(path)
#else
    #include <unistd.h>
    #include <sys/stat.h>
    #define GETCWD getcwd
    #define MKDIR(path) mkdir(path, 0755)
#endif

int is_safe_relative_path(const char *path) {
    if (!path || !*path || path[0] == '/' || path[0] == '\\' || strchr(path, ':')) return 0;
    for (const char *p = path; *p; ++p) {
        if (*p == '\\') return 0;
        if (*p == '.' && (p == path || p[-1] == '/') && p[1] == '.' && (p[2] == '/' || p[2] == '\0')) return 0;
    }
    return 1;
}

int generate_file(const char *filename, const char *content) {
    if (!is_safe_relative_path(filename)) {
        fprintf(stderr, "Unsafe output path rejected: %s\n", filename ? filename : "(null)");
        return ERROR;
    }
    FILE *f = fopen(filename, "w");
    if (!f) {
        perror("File Error");
        return ERROR;
    }
    fputs(content, f);
    fclose(f);
    return SUCCESS;
}

int create_directory(const char *dirname) {
    if (!is_safe_relative_path(dirname)) {
        fprintf(stderr, "Unsafe directory path rejected: %s\n", dirname ? dirname : "(null)");
        return ERROR;
    }
    if (MKDIR(dirname) != 0) {
        perror("Directory Error");
        return ERROR;
    }
    return SUCCESS;
}

int check_python() {
    const char* cmd = 
#ifdef _WIN32
        "python --version >nul 2>&1 || py --version >nul 2>&1";
#else
        "python3 --version >/dev/null 2>&1 || python --version >/dev/null 2>&1";
#endif
    return (system(cmd) == 0) ? SUCCESS : ERROR;
}

void get_curr_dir(char *buf, int size) {
    if (buf && size > 0) {
        GETCWD(buf, size);
    }
}
