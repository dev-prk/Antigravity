import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        while (scanner.hasNext()) {
            String name = scanner.next();
            
            if (scanner.hasNextInt()) {
                int age = scanner.nextInt();
                Person person = new Person();
                person.setName(name);
                person.setAge(age);
                
                if (person.getAge() > 0) {
                    System.out.println("Name: " + person.getName());
                    System.out.println("Age: " + person.getAge());
                } else {
                    System.out.println("Invalid age");
                }
            }
        }
        
        scanner.close();
    }
}

class Person {
    private String name;
    private int age;
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getName() {
        return name;
    }
    
    public void setAge(int age) {
        if (age > 0) {
            this.age = age;
        } else {
            this.age = 0;
        }
    }
    
    public int getAge() {
        return age;
    }
}
