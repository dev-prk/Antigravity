import java.io.*;
import java.util.*;

interface AudioPlayer {
    void playAudio();
}

interface VideoPlayer {
    void playVideo();
}

class MediaCenter implements AudioPlayer, VideoPlayer {
    private String fileName;
    
    public MediaCenter(String fileName) {
        this.fileName = fileName;
    }
    
    @Override
    public void playAudio() {
        System.out.println("Audio file detected: Playing with 128kbps quality");
    }
    
    @Override
    public void playVideo() {
        System.out.println("Video file detected: Playing at 1080p resolution");
    }
    
    public void detectAndPlay() {
        if (fileName == null || fileName.isEmpty()) {
            return;
        }
        
        String lowerFileName = fileName.toLowerCase();
        
        String[] audioExtensions = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"};
        for (String ext : audioExtensions) {
            if (lowerFileName.endsWith(ext)) {
                playAudio();
                return;
            }
        }
        
        String[] videoExtensions = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"};
        for (String ext : videoExtensions) {
            if (lowerFileName.endsWith(ext)) {
                playVideo();
                return;
            }
        }
    }
}

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        
        if (line != null) {
            line = line.trim();
        }
        
        MediaCenter mediaCenter = new MediaCenter(line);
        mediaCenter.detectAndPlay();
    }
}
