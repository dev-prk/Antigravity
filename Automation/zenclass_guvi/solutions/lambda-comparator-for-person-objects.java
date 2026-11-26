import java.util.*;
import java.util.function.Function;

class Person {
    String name;
    int age;
    
    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public String toString() {
        return name + " " + age;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        sc.nextLine(); // Consume the newline
        
        List<Person> people = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            String line = sc.nextLine();
            String[] parts = line.split(" ");
            String name = parts[0];
            int age = Integer.parseInt(parts[1]);
            people.add(new Person(name, age));
        }
        
        // Sort using lambda: age descending, name ascending
        people.sort((p1, p2) -> {
            if (p1.age != p2.age) {
                return Integer.compare(p2.age, p1.age); // descending
            }
            return p1.name.compareTo(p2.name); // ascending
        });
        
        for (Person p : people) {
            System.out.println(p);
        }
    }
}
