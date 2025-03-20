package net.kpuig.nnqueue.service;

import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.File;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.FileSystemResource;
import org.springframework.stereotype.Service;

import net.kpuig.nnqueue.service.data.*;

@Service
public class FileHandlingService {
    @Autowired private FileIdService fileIdService;

    public FileId enqueueFile(String fileName, InputStream byteStream) {
        FileId id = fileIdService.generateId();

        // Type your own implementation here

        return id;
    }

    public FileStatus getStatus(String id, String fileName) {
        return null;
    }

    public FileSystemResource getDownloadableFileResource(String id, String fileName) {
        // Type your own implementation here
        return null;
    }
}
