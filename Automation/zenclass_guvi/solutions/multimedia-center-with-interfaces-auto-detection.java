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
    private String extension;
    
    public MediaCenter(String fileName) {
        this.fileName = fileName;
        this.extension = getFileExtension(fileName);
    }
    
    private String getFileExtension(String fileName) {
        if (fileName == null || fileName.isEmpty()) {
            return "";
        }
        int dotIndex = fileName.lastIndexOf('.');
        if (dotIndex == -1 || dotIndex == fileName.length() - 1) {
            return "";
        }
        return fileName.substring(dotIndex + 1).toLowerCase();
    }
    
    public void detectAndPlay() {
        if (isAudioFile()) {
            playAudio();
        } else if (isVideoFile()) {
            playVideo();
        }
    }
    
    private boolean isAudioFile() {
        Set<String> audioExtensions = new HashSet<>(Arrays.asList(
            "mp3", "wav", "aac", "flac", "ogg", "wma", "m4a", "aiff"
        ));
        return audioExtensions.contains(extension);
    }
    
    private boolean isVideoFile() {
        Set<String> videoExtensions = new HashSet<>(Arrays.asList(
            "mp4", "avi", "mkv", "mov", "wmv", "flv", "webm", "m4v"
        ));
        return videoExtensions.contains(extension);
    }
    
    @Override
    public void playAudio() {
        System.out.println("Audio file detected: Playing with 128kbps quality");
    }
    
    @Override
    public void playVideo() {
        System.out.println("Video file detected: Playing at 1080p resolution");
    }
}

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();
        
        if (line != null) {
            line = line.trim();
        }
        
        MediaCenter mediaCenter = new MediaCenter(line != null ? line : "");
        mediaCenter.detectAndPlay();
    }
}
