#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_TITLE_LEN 101
#define MAX_AUTHOR_LEN 101

typedef struct {
    char title[MAX_TITLE_LEN];
    char author[MAX_AUTHOR_LEN];
    int year;
} Book;

int main(void) {
    int n;
    if (scanf("%d", &n) != 1 || n < 1) {
        return 0;
    }
    
    Book *books = malloc(n * sizeof(Book));
    if (books == NULL) {
        return 0;
    }
    
    for (int i = 0; i < n; i++) {
        scanf("%100s %100s %d", books[i].title, books[i].author, &books[i].year);
    }
    
    for (int i = 0; i < n; i++) {
        printf("Title: %s, Author: %s, Year: %d\n", books[i].title, books[i].author, books[i].year);
    }
    
    free(books);
    return 0;
}
