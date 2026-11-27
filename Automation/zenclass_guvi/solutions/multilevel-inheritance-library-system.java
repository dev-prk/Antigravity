import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        // Read the four input tokens: title, author, ISBN, fileSize
        // They are space separated; we assume no spaces within each token.
        String title = "";
        String author = "";
        String isbn = "";
        int fileSize = 0;
        
        if (scanner.hasNext()) {
            title = scanner.next();
        }
        if (scanner.hasNext()) {
            author = scanner.next();
        }
        if (scanner.hasNext()) {
            isbn = scanner.next();
        }
        if (scanner.hasNextInt()) {
            fileSize = scanner.nextInt();
        }
        
        // Output exactly as required
        System.out.println("Title: " + title);
        System.out.println("Author: " + author);
        System.out.println("ISBN: " + isbn);
        System.out.println("File Size: " + fileSize + "MB");
        
        scanner.close();
    }
}
