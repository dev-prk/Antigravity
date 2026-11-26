#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_NAME_LEN 100

typedef struct Song {
    char name[MAX_NAME_LEN];
    int duration;
    struct Song *next;
    struct Song *prev;
} Song;

int main() {
    int Q;
    if (scanf("%d", &Q) != 1) return 0;
    
    Song *head = NULL;
    Song *tail = NULL;
    Song *current = NULL;
    
    int maxDuration = 0;
    
    for (int q = 0; q < Q; q++) {
        char op[10];
        if (scanf("%s", op) != 1) break;
        
        if (strcmp(op, "ADD") == 0) {
            char name[MAX_NAME_LEN];
            int duration;
            if (scanf("%s %d", name, &duration) == 2) {
                Song *newSong = (Song *)malloc(sizeof(Song));
                if (!newSong) continue;
                
                strcpy(newSong->name, name);
                newSong->duration = duration;
                newSong->next = NULL;
                newSong->prev = tail;
                
                if (tail) {
                    tail->next = newSong;
                } else {
                    head = newSong;
                }
                tail = newSong;
                
                if (duration > maxDuration) {
                    maxDuration = duration;
                }
                
                if (current == NULL) {
                    current = newSong;
                }
            }
        } else if (strcmp(op, "DELETE") == 0) {
            char name[MAX_NAME_LEN];
            if (scanf("%s", name) != 1) continue;
            
            Song *temp = head;
            int found = 0;
            while (temp) {
                if (strcmp(temp->name, name) == 0) {
                    found = 1;
                    Song *prevNode = temp->prev;
                    Song *nextNode = temp->next;
                    
                    if (prevNode) {
                        prevNode->next = nextNode;
                    } else {
                        head = nextNode;
                    }
                    
                    if (nextNode) {
                        nextNode->prev = prevNode;
                    } else {
                        tail = prevNode;
                    }
                    
                    if (temp == current) {
                        current = nextNode ? nextNode : prevNode;
                    }
                    
                    free(temp);
                    break;
                }
                temp = temp->next;
            }
            
            if (!found) {
                printf("Song not found\n");
            }
        } else if (strcmp(op, "NEXT") == 0) {
            if (current && current->next) {
                current = current->next;
            } else {
                printf("No next song\n");
            }
        } else if (strcmp(op, "PREV") == 0) {
            if (current && current->prev) {
                current = current->prev;
            } else {
                printf("No previous song\n");
            }
        } else if (strcmp(op, "PRINT") == 0) {
            if (current == NULL) {
                printf("\n");
            } else {
                Song *temp = current;
                int first = 1;
                while (temp) {
                    if (!first) {
                        printf(" ");
                    }
                    printf("%s", temp->name);
                    first = 0;
                    temp = temp->next;
                }
                printf("\n");
            }
        }
    }
    
    // Free memory
    Song *temp = head;
    while (temp) {
        Song *next = temp->next;
        free(temp);
        temp = next;
    }
    
    return 0;
}
