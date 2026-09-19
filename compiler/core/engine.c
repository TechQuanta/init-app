#include <stdio.h>
#include <string.h>
#include "engine.h"
#include "../platform/actions.h"
#include "../utils.h"

int run_engine(const char *config_path) {
    FILE *f = fopen(config_path, "r");
    if (!f) {
        printf("[!] Error: Could not open config file: %s\n", config_path);
        return ERROR;
    }

    char line[1024];
    while (fgets(line, sizeof(line), f)) {
        trim_newline(line);
        
        // Skip empty lines or comments
        if (line[0] == '\0' || line[0] == '#') continue;

        if (starts_with(line, "DIR=")) {
            char *dirname = line + 4;
            printf("[Action] Creating directory: %s\n", dirname);
            if (create_directory(dirname) != SUCCESS) {
                fclose(f);
                return ERROR;
            }
        } else if (starts_with(line, "FILE=")) {
            char *data = line + 5;
            char *sep = strchr(data, '|');
            if (sep) {
                *sep = '\0';
                char *filename = data;
                char *content = sep + 1;
                printf("[Action] Creating: %s\n", filename);
                if (generate_file(filename, content) != SUCCESS) {
                    fclose(f);
                    return ERROR;
                }
            } else {
                fprintf(stderr, "Invalid FILE record; expected FILE=relative/path|content\n");
                fclose(f);
                return ERROR;
            }
        } else {
            fprintf(stderr, "Unsupported record. Only DIR= and FILE= are accepted.\n");
            fclose(f);
            return ERROR;
        }
    }

    fclose(f);
    return SUCCESS;
}
