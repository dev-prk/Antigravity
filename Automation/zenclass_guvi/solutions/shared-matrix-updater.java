import java.util.concurrent.locks.ReentrantLock;

public class Main {
    public static void main(String[] args) throws Exception {
        java.util.Scanner scanner = new java.util.Scanner(System.in);
        
        int rows = scanner.nextInt();
        int cols = scanner.nextInt();
        
        int[][] matrix = new int[rows][cols];
        ReentrantLock[] locks = new ReentrantLock[rows];
        for (int i = 0; i < rows; i++) {
            locks[i] = new ReentrantLock();
        }
        
        java.util.List<Integer> rowValues = new java.util.ArrayList<>();
        java.util.List<Integer> colValues = new java.util.ArrayList<>();
        
        while (scanner.hasNextInt()) {
            int row = scanner.nextInt();
            int value = scanner.nextInt();
            rowValues.add(row);
            colValues.add(value);
        }
        
        java.util.concurrent.ExecutorService executor = java.util.concurrent.Executors.newCachedThreadPool();
        
        for (int i = 0; i < rowValues.size(); i++) {
            final int row = rowValues.get(i);
            final int value = colValues.get(i);
            executor.submit(new Runnable() {
                public void run() {
                    locks[row].lock();
                    try {
                        for (int j = 0; j < cols; j++) {
                            matrix[row][j] = value;
                        }
                    } finally {
                        locks[row].unlock();
                    }
                }
            });
        }
        
        executor.shutdown();
        executor.awaitTermination(1, java.util.concurrent.TimeUnit.MINUTES);
        
        for (int i = 0; i < rows; i++) {
            System.out.print("[");
            for (int j = 0; j < cols; j++) {
                if (j > 0) System.out.print(", ");
                System.out.print(matrix[i][j]);
            }
            System.out.println("]");
        }
        
        scanner.close();
    }
}
