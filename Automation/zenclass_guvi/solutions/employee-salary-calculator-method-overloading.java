import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws NumberFormatException {
        Scanner sc = new Scanner(System.in);
        
        int baseSalary = Integer.parseInt(sc.nextLine().trim());
        
        int bonus = 0;
        int deductions = 0;
        boolean hasBonus = false;
        boolean hasDeductions = false;
        
        if (sc.hasNextLine()) {
            String bonusLine = sc.nextLine().trim();
            if (!bonusLine.isEmpty()) {
                bonus = Integer.parseInt(bonusLine);
                hasBonus = true;
            }
        }
        
        if (sc.hasNextLine()) {
            String deductLine = sc.nextLine().trim();
            if (!deductLine.isEmpty()) {
                deductions = Integer.parseInt(deductLine);
                hasDeductions = true;
            }
        }
        
        Employee emp = new Employee();
        int result;
        
        if (hasBonus && hasDeductions) {
            result = emp.calculateSalary(baseSalary, bonus, deductions);
        } else if (hasBonus) {
            result = emp.calculateSalary(baseSalary, bonus);
        } else {
            result = emp.calculateSalary(baseSalary);
        }
        
        System.out.println(result);
    }
}

class Employee {
    public int calculateSalary(int baseSalary) {
        return baseSalary;
    }
    
    public int calculateSalary(int baseSalary, int bonus) {
        return baseSalary + bonus;
    }
    
    public int calculateSalary(int baseSalary, int bonus, int deductions) {
        return baseSalary + bonus - deductions;
    }
}
