import java.util.Scanner;

class Student {
    protected String name;
    protected int rollNumber;
    protected int marks;
    
    public Student(String name, int rollNumber, int marks) {
        this.name = name;
        this.rollNumber = rollNumber;
        this.marks = marks;
    }
    
    public String getGrade() {
        if (marks >= 90 && marks <= 100) {
            return "A";
        } else if (marks >= 75 && marks <= 89) {
            return "B";
        } else if (marks >= 50 && marks <= 74) {
            return "C";
        } else {
            return "Fail";
        }
    }
}

class GraduateStudent extends Student {
    private String thesisTitle;
    
    public GraduateStudent(String name, int rollNumber, int marks, String thesisTitle) {
        super(name, rollNumber, marks);
        this.thesisTitle = thesisTitle;
    }
    
    public String getThesisTitle() {
        return thesisTitle;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        String name = sc.nextLine();
        int rollNumber = sc.nextInt();
        int marks = sc.nextInt();
        sc.nextLine(); // consume the newline
        String thesisTitle = sc.nextLine();
        
        GraduateStudent gs = new GraduateStudent(name, rollNumber, marks, thesisTitle);
        
        System.out.println(gs.getGrade());
        System.out.println(gs.getThesisTitle());
    }
}
