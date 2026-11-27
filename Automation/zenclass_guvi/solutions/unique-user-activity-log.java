import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = Integer.parseInt(sc.nextLine());
        
        Map<String, Set<String>> userActivities = new TreeMap<>();
        
        for (int i = 0; i < n; i++) {
            String line = sc.nextLine();
            String[] parts = line.split(" ", 3);
            String command = parts[0];
            
            if (command.equals("ADD_ACTIVITY")) {
                String userId = parts[1];
                String activity = parts[2];
                userActivities.computeIfAbsent(userId, k -> new TreeSet<>()).add(activity);
            } else if (command.equals("DISPLAY_ACTIVITIES")) {
                String userId = parts[1];
                Set<String> activities = userActivities.get(userId);
                if (activities == null || activities.isEmpty()) {
                    System.out.println("No activities found.");
                } else {
                    for (String act : activities) {
                        System.out.println(act);
                    }
                }
            }
        }
        sc.close();
    }
}
