import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;

public class Main {
    static class Person {
        String name;
        int age;

        Person(String name, int age) {
            this.name = name;
            this.age = age;
        }

        void addYears(int years) {
            this.age += years;
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        String name = reader.readLine();
        int age = Integer.parseInt(reader.readLine().trim());
        int yearsToAdd = Integer.parseInt(reader.readLine().trim());

        Person person = new Person(name, age);
        person.addYears(yearsToAdd);

        System.out.println(person.age);
    }
}
