import java.io.*;
import java.util.*;

public class Main {
    static class UnionFind {
        Map<String, String> parent;
        Map<String, Double> weight;
        
        public UnionFind() {
            parent = new HashMap<>();
            weight = new HashMap<>();
        }
        
        public void add(String x) {
            if (!parent.containsKey(x)) {
                parent.put(x, x);
                weight.put(x, 1.0);
            }
        }
        
        public String find(String x) {
            if (!parent.get(x).equals(x)) {
                String root = find(parent.get(x));
                weight.put(x, weight.get(x) * weight.get(parent.get(x)));
                parent.put(x, root);
            }
            return parent.get(x);
        }
        
        public double getValue(String x, String root) {
            find(x);
            String actualRoot = find(root);
            if (!actualRoot.equals(find(root))) {
                return 0;
            }
            double result = weight.get(x);
            String r = root;
            while (!r.equals(parent.get(r))) {
                result *= weight.get(r);
                r = parent.get(r);
            }
            result *= weight.get(r);
            return result;
        }
        
        public double getValueFromPath(String x, String root) {
            Map<String, Double> pathWeight = new HashMap<>();
            pathWeight.put(x, 1.0);
            
            String curr = x;
            while (!parent.get(curr).equals(curr)) {
                String next = parent.get(curr);
                pathWeight.put(next, pathWeight.get(curr) * weight.get(curr));
                curr = next;
            }
            
            String rootNode = curr;
            
            if (parent.get(root).equals(root)) {
                double rootVal = 1.0;
                curr = root;
                while (!parent.get(curr).equals(curr)) {
                    rootVal *= weight.get(curr);
                    curr = parent.get(curr);
                }
                rootVal *= weight.get(curr);
                return pathWeight.get(rootNode) / rootVal;
            }
            
            return 0;
        }
        
        public void union(String a, String b, double value) {
            add(a);
            add(b);
            
            String rootA = find(a);
            String rootB = find(b);
            
            if (!rootA.equals(rootB)) {
                double ratio = value * weight.get(b) / weight.get(a);
                parent.put(rootA, rootB);
                weight.put(rootA, ratio);
            }
        }
        
        public double query(String a, String b) {
            add(a);
            add(b);
            
            if (!find(a).equals(find(b))) {
                return -1.0;
            }
            
            double result = weight.get(a) / weight.get(b);
            return result;
        }
    }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        UnionFind uf = new UnionFind();
        
        int n = sc.nextInt();
        for (int i = 0; i < n; i++) {
            String a = sc.next();
            String b = sc.next();
            double val = sc.nextDouble();
            uf.union(a, b, val);
        }
        
        int q = sc.nextInt();
        for (int i = 0; i < q; i++) {
            String a = sc.next();
            String b = sc.next();
            double result = uf.query(a, b);
            System.out.println(result);
        }
        
        sc.close();
    }
}
