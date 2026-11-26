import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        float f1 = sc.nextFloat();
        float f2 = sc.nextFloat();
        
        int n1 = (int) f1;
        int n2 = (int) f2;
        
        //..... YOUR CODE STARTS HERE .....
        
        int andResult = n1 & n2;
        int orResult = n1 | n2;
        int xorResult = n1 ^ n2;
        int notAndResult = (~n1) & n2;
        
        System.out.println("Bitwise AND result: " + andResult);
        System.out.println("Bitwise OR result: " + orResult);
        System.out.println("Bitwise XOR result: " + xorResult);
        System.out.println("Bitwise NOT and AND result: " + notAndResult);
        
        //..... YOUR CODE ENDS HERE .....
    }
}
