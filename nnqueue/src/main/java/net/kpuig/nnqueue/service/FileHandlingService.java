package net.kpuig.nnqueue.service;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.FileSystemResource;
import org.springframework.stereotype.Service;

import net.kpuig.nnqueue.service.data.*;

@Service
public class FileHandlingService {
    private static final String QUEUE_ROOT_DIRECTORY = "process_queue/";
    
    private static final String ENQUEUE_DIRECTORY = QUEUE_ROOT_DIRECTORY + "queue/";
    private static final String ERROR_DIRECTORY = QUEUE_ROOT_DIRECTORY + "error/";
    private static final String PROCESSING_DIRECTORY = QUEUE_ROOT_DIRECTORY + "processing/";
    private static final String PROCESSED_DIRECTORY = QUEUE_ROOT_DIRECTORY + "processed/";
    private static final String TEMP_DIRECTORY = QUEUE_ROOT_DIRECTORY + "temp/";
    
    private static final String PROCESSED_VIDEO_EXTENSION = ".mp4";

    private FileIdService fileIdService;

    public FileHandlingService(@Autowired FileIdService fileIdService) throws Exception {
        this.fileIdService = fileIdService;
        initializeQueueDirectories();
    }

    public String enqueueFile(InputStream byteStream) throws IOException {
        // Create a new file name
        FileId id = fileIdService.generateId();
        String fileName = id.getId() + PROCESSED_VIDEO_EXTENSION;

        // Save file to appropriate directory
        File file = new File(TEMP_DIRECTORY + fileName);
        if (file.exists()) {
            return null;
        }
        if (!file.createNewFile()) {
            return null;
        }
        FileOutputStream fileOut = new FileOutputStream(file);
        byte[] buffer = new byte[8192];
        int bytesRead;
        while ((bytesRead = byteStream.read(buffer)) > 0) {
            fileOut.write(buffer, 0, bytesRead);
        }
        fileOut.flush();
        fileOut.close();

        Files.move(file.toPath(), new File(ENQUEUE_DIRECTORY + fileName).toPath());

        return fileName;
    }

    public FileStatus getStatus(String fileName) {
        File file = new File(PROCESSED_DIRECTORY + fileName);
        if (file.exists()) {
            return FileStatus.PROCESSED;
        }

        file = new File(PROCESSING_DIRECTORY + fileName);
        if (file.exists()) {
            return FileStatus.PROCESSING;
        }

        file = new File(ERROR_DIRECTORY + fileName);
        if (file.exists()) {
            return FileStatus.ERROR;
        }

        file = new File(ENQUEUE_DIRECTORY + fileName);
        if (file.exists()) {
            return FileStatus.QUEUED;
        }

        return FileStatus.NOTFOUND;
    }

    public FileSystemResource getDownloadableFileResource(String fileName) {
        if (getStatus(fileName) != FileStatus.PROCESSED)
            return null;
        
        File downloadFile = new File(PROCESSED_DIRECTORY + fileName);
        FileSystemResource resource = new FileSystemResource(downloadFile);
        return resource;
    }

    private static void initializeQueueDirectories() throws Exception {
        File file = new File(PROCESSED_DIRECTORY);
        file.mkdirs();

        file = new File(PROCESSING_DIRECTORY);
        file.mkdirs();

        file = new File(ERROR_DIRECTORY);
        file.mkdirs();

        file = new File(ENQUEUE_DIRECTORY);
        file.mkdirs();

        file = new File(TEMP_DIRECTORY);
        file.mkdirs();
    }

}
