package net.kpuig.nnqueue.service;

import java.util.UUID;

import org.springframework.stereotype.Service;

import net.kpuig.nnqueue.service.data.FileId;

@Service
public class FileIdService {
    public FileId generateId() {
        FileId fileId = new FileId();
        fileId.setId(UUID.randomUUID().toString());
        return fileId;
    }
}
