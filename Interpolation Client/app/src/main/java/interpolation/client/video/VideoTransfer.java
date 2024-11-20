package interpolation.client.video;

import java.io.File;

public class VideoTransfer {
    private String domain;

    public VideoTransfer(String domain) {
        this.domain = domain;
    }

    // Returns the filename that will be downloaded once processing is done
    public String uploadVideo(File video) {
        if (domain != null) {
            return domain + "/upload/" + video.getName(); // Simulated URL for uploaded video
        }
        return null;
    }

    // True if serverVideo exists on server and download successful, False otherwise
    public boolean downloadVideo(String serverVideo, File output) {
        if (domain != null) {
            System.out.println("Downloading: " + domain + "/videos/" + serverVideo);
            return true; // Simulate successful download
        }
        return false;
    }

    // True if serverVideo exists on server
    public boolean videoExists(String serverVideo) {
        if (domain != null) {
            System.out.println("Checking existence of: " + domain + "/videos/" + serverVideo);
            return true; // Simulate video existence
        }
        return false;
    }

    // Getter for domain
    public String getDomain() {
        return domain;
    }
}

