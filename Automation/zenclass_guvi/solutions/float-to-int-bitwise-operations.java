import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        float float1 = scanner.nextFloat();
        float float2 = scanner.nextFloat();
        
        int int1 = (int) float1;
        int int2 = (int) float2;
        
        int andResult = int1 & int2;
        int orResult = int1 | int2;
        int xorResult = int1 ^ int2;
        int notAndResult = (~int1) & int2;
        
        System.out.println("Bitwise AND result: " + andResult);
        System.out.println("Bitwise OR result: " + orResult);
        System.out.println("Bitwise XOR result: " + xorResult);
        System.out.println("Bitwise NOT and AND result: " + notAndResult);
        
        scanner.close();
    }
}
