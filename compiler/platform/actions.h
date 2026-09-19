#ifndef ACTIONS_H
#define ACTIONS_H

int generate_file(const char *filename, const char *content);
int create_directory(const char *dirname);
int is_safe_relative_path(const char *path);
int check_python();
void get_curr_dir(char *buf, int size);

#endif
