import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line;
        
        line = br.readLine();
        while (line != null && line.trim().isEmpty()) {
            line = br.readLine();
        }
        if (line == null) return;
        long registeredVoters = Long.parseLong(line.trim());
        
        line = br.readLine();
        while (line != null && line.trim().isEmpty()) {
            line = br.readLine();
        }
        if (line == null) return;
        long numCandidates = Long.parseLong(line.trim());
        
        line = br.readLine();
        while (line != null && line.trim().isEmpty()) {
            line = br.readLine();
        }
        if (line == null) return;
        long numVotes = Long.parseLong(line.trim());
        
        long votesCast = 0;
        for (long i = 0; i < numVotes; i++) {
            line = br.readLine();
            while (line != null && line.trim().isEmpty()) {
                line = br.readLine();
            }
            if (line == null) break;
            
            long candidateId = Long.parseLong(line.trim());
            
            if (votesCast < registeredVoters && candidateId >= 1 && candidateId <= numCandidates) {
                System.out.println("VALID");
                votesCast++;
            } else {
                System.out.println("INVALID");
            }
        }
    }
}
