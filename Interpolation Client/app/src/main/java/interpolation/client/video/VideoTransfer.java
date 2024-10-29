package interpolation.client.video;

import java.io.File;

public class VideoTransfer {
    private String domain;

    public VideoTransfer(String domain) {
        this.domain = domain;
    }

    // Returns the filename that will be downloaded once processing is done
    public String uploadVideo(File video) {
        return null;
    }

    // True if serverVideo exists on server and download successful, False otherwise
    public boolean downloadVideo(String serverVideo, File output) {
        return false;
    }

    // True if serverVideo exists on server
    public boolean videoExists(String serverVideo) {
        return false;
    }
}
