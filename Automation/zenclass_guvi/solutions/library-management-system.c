#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int id;
    char title[256];
} Book;

int find_book_index(Book *books, int count, int id) {
    for (int i = 0; i < count; ++i) {
        if (books[i].id == id) return i;
    }
    return -1;
}

int main(void) {
    Book *books = NULL;
    int capacity = 0;
    int count = 0;
    int choice;

    while (scanf("%d", &choice) == 1) {
        if (choice == 1) { /* Add a book */
            int id;
            char buffer[256];
            
            /* Read book ID */
            if (scanf("%d", &id) != 1) break;
            
            /* Read title: consume the newline after the ID, then read until newline */
            /* We need to carefully handle the remaining line */
            /* First, discard the rest of the line after the ID (which should be just newline or spaces) */
            int c;
            while ((c = getchar()) != EOF && c != '\n') {
                /* skip until newline */
            }
            
            /* Now read the title line */
            if (fgets(buffer, sizeof(buffer), stdin) == NULL) break;
            
            /* Remove trailing newline if present */
            size_t len = strlen(buffer);
            if (len > 0 && buffer[len - 1] == '\n') {
                buffer[len - 1] = '\0';
                len--;
            }
            /* Also remove any trailing carriage return if present (for Windows line endings) */
            if (len > 0 && buffer[len - 1] == '\r') {
                buffer[len - 1] = '\0';
            }
            
            /* Check if book ID already exists */
            int existing = find_book_index(books, count, id);
            if (existing != -1) {
                /* Update existing book */
                snprintf(books[existing].title, sizeof(books[existing].title), "%s", buffer);
            } else {
                /* Add new book */
                if (count >= capacity) {
                    capacity = (capacity == 0) ? 10 : capacity * 2;
                    Book *new_books = (Book *)realloc(books, capacity * sizeof(Book));
                    if (new_books == NULL) {
                        free(books);
                        books = NULL;
                        return 1;
                    }
                    books = new_books;
                }
                books[count].id = id;
                snprintf(books[count].title, sizeof(books[count].title), "%s", buffer);
                count++;
            }
            printf("Book added successfully.\n");
        } 
        else if (choice == 2) { /* Search for a book */
            int id;
            if (scanf("%d", &id) != 1) break;
            
            int idx = find_book_index(books, count, id);
            if (idx != -1) {
                printf("Book found: ID=%d, Title=\"%s\"\n", books[idx].id, books[idx].title);
            } else {
                printf("Book not found.\n");
            }
        } 
        else if (choice == 3) { /* Delete a book */
            int id;
            if (scanf("%d", &id) != 1) break;
            
            int idx = find_book_index(books, count, id);
            if (idx != -1) {
                /* Remove the book by shifting elements */
                for (int i = idx; i < count - 1; ++i) {
                    books[i] = books[i + 1];
                }
                count--;
                printf("Book deleted successfully.\n");
            } else {
                printf("Book not found.\n");
            }
        } 
        else if (choice == 4) { /* Display all books */
            if (count == 0) {
                printf("No books in the library.\n");
            } else {
                for (int i = 0; i < count; ++i) {
                    printf("Book ID=%d, Title=\"%s\"\n", books[i].id, books[i].title);
                }
            }
        } 
        else if (choice == 5) { /* Exit */
            printf("Exiting the program...\n");
            break;
        }
    }
    
    if (books != NULL) {
        free(books);
    }
    
    return 0;
}
