import java.io.*;
import java.util.*;

public class Main {
    static class Job {
        int id, cpu, memory;
        Job(int id, int cpu, int memory) {
            this.id = id;
            this.cpu = cpu;
            this.memory = memory;
        }
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        
        Map<Integer, Job> jobs = new HashMap<>();
        List<Job> jobList = new ArrayList<>();
        Set<Integer> removedIds = new HashSet<>();
        
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int op = Integer.parseInt(st.nextToken());
            
            if (op == 1) {
                int id = Integer.parseInt(st.nextToken());
                int cpu = Integer.parseInt(st.nextToken());
                int memory = Integer.parseInt(st.nextToken());
                Job j = new Job(id, cpu, memory);
                jobs.put(id, j);
                jobList.add(j);
            } else if (op == 2) {
                int id = Integer.parseInt(st.nextToken());
                int cpu = Integer.parseInt(st.nextToken());
                int memory = Integer.parseInt(st.nextToken());
                if (jobs.containsKey(id)) {
                    jobs.get(id).cpu = cpu;
                    jobs.get(id).memory = memory;
                }
            } else if (op == 3) {
                int id = Integer.parseInt(st.nextToken());
                if (jobs.containsKey(id)) {
                    jobs.remove(id);
                    removedIds.add(id);
                }
            } else if (op == 4) {
                List<Job> activeJobs = new ArrayList<>();
                for (Job j : jobList) {
                    if (!removedIds.contains(j.id) && jobs.containsKey(j.id)) {
                        activeJobs.add(j);
                    }
                }
                activeJobs.sort((a, b) -> {
                    if (a.cpu != b.cpu) return b.cpu - a.cpu;
                    return b.memory - a.memory;
                });
                for (Job j : activeJobs) {
                    System.out.println("(" + j.id + ", " + j.cpu + ", " + j.memory + ")");
                }
            } else if (op == 5) {
                Job maxJob = null;
                for (Job j : jobs.values()) {
                    if (removedIds.contains(j.id)) continue;
                    if (maxJob == null) {
                        maxJob = j;
                    } else {
                        if (j.cpu > maxJob.cpu || (j.cpu == maxJob.cpu && j.memory > maxJob.memory)) {
                            maxJob = j;
                        }
                    }
                }
                if (maxJob != null) {
                    System.out.println("Job with max usage: (" + maxJob.id + ", " + maxJob.cpu + ", " + maxJob.memory + ")");
                }
            }
        }
    }
}
