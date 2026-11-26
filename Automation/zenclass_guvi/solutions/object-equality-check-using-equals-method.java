import java.io.*;
import java.util.*;

class Person {
    private String name;
    private int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && Objects.equals(name, person.name);
    }
}

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        String line1 = br.readLine();
        if (line1 == null || line1.trim().isEmpty()) {
            String line2 = br.readLine();
            System.out.println("Not Equal");
            return;
        }
        
        String[] parts1 = line1.trim().split("\\s+");
        String name1 = parts1[0];
        int age1 = Integer.parseInt(parts1[1]);
        
        String line2 = br.readLine();
        if (line2 == null || line2.trim().isEmpty()) {
            System.out.println("Not Equal");
            return;
        }
        
        String[] parts2 = line2.trim().split("\\s+");
        String name2 = parts2[0];
        int age2 = Integer.parseInt(parts2[1]);
        
        Person p1 = new Person(name1, age1);
        Person p2 = new Person(name2, age2);
        
        if (p1.equals(p2)) {
            System.out.println("Equal");
        } else {
            System.out.println("Not Equal");
        }
    }
}
