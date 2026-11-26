import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

interface Animal {
    String speak();
}

class Lion implements Animal {
    @Override
    public String speak() {
        return "Roar";
    }
}

class Elephant implements Animal {
    @Override
    public String speak() {
        return "Trumpet";
    }
}

class Monkey implements Animal {
    @Override
    public String speak() {
        return "Ooh Ooh Aah Aah";
    }
}

public class Main {
    public static void main(String[] args) {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        try {
            String line = br.readLine();
            if (line == null || line.trim().isEmpty()) {
                return;
            }
            int n = Integer.parseInt(line.trim());
            List<Animal> zoo = new ArrayList<>(n);
            for (int i = 0; i < n; i++) {
                String type = br.readLine();
                if (type == null) break;
                type = type.trim();
                Animal animal;
                switch (type) {
                    case "Lion":
                        animal = new Lion();
                        break;
                    case "Elephant":
                        animal = new Elephant();
                        break;
                    case "Monkey":
                        animal = new Monkey();
                        break;
                    default:
                        // According to problem, only these three types appear.
                        // If an unknown type appears, we skip or handle as needed.
                        continue;
                }
                zoo.add(animal);
            }
            StringBuilder sb = new StringBuilder();
            for (Animal a : zoo) {
                sb.append(a.speak()).append('\n');
            }
            System.out.print(sb.toString());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
