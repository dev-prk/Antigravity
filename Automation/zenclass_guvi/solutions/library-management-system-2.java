import java.util.*;

interface BookOperations {
    void addBook(String book);
}

interface UserOperations {
    void borrowBook(String book);
}

class Library implements BookOperations, UserOperations {
    private List<String> books = new ArrayList<>();

    @Override
    public void addBook(String book) {
        books.add(book);
        System.out.println("Book added: " + book);
    }

    @Override
    public void borrowBook(String book) {
        if (books.contains(book)) {
            books.remove(book);
            System.out.println("Book borrowed: " + book);
        } else {
            System.out.println("Book not available");
        }
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        Library lib = new Library();
        String bookToAdd = sc.nextLine();
        lib.addBook(bookToAdd);
        String borrowLine = sc.nextLine();
        String[] parts = borrowLine.split(" ", 2);
        String bookToBorrow = parts[1];
        lib.borrowBook(bookToBorrow);
        sc.close();
    }
}
