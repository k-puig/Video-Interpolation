package net.kpuig.nnqueue.controller;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import net.kpuig.nnqueue.controller.response.FileDataResponse;
import net.kpuig.nnqueue.controller.response.FileStatusResponse;
import net.kpuig.nnqueue.service.FileHandlingService;
import net.kpuig.nnqueue.service.data.FileId;

import java.io.IOException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;


@RestController
@RequestMapping("/queue")
public class QueueController {
    private final long maxFileSize = 200000000; // 200 MB
    @Autowired private FileHandlingService queueService;

    @PostMapping("/upload")
    public ResponseEntity<FileDataResponse> uploadVideo(@RequestParam MultipartFile file) throws IOException {
        if (file.getSize() > maxFileSize)
            return ResponseEntity.badRequest().body(null);
        FileId id = queueService.enqueueFile(file.getOriginalFilename(), file.getInputStream());
        
        FileDataResponse response = new FileDataResponse();
        response.setId(id.getId());
        response.setFileName(file.getOriginalFilename());
        return ResponseEntity.ok().body(response);
    }

    @GetMapping("/status/{id}/{file}")
    public ResponseEntity<FileStatusResponse> getFileStatus(@PathVariable String id, @PathVariable String file) {
        return null;
    }

    @GetMapping("/download/{id}/{file}")
    public ResponseEntity<Resource> downloadFile() {
        return null;
    }

}
