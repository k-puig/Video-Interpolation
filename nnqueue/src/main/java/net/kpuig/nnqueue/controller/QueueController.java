package net.kpuig.nnqueue.controller;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import net.kpuig.nnqueue.controller.response.FileDataResponse;
import net.kpuig.nnqueue.controller.response.FileStatusResponse;
import net.kpuig.nnqueue.service.FileHandlingService;
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
        /* // Restrict file size */
        /* if (file.getSize() > maxFileSize) */
        /*     return ResponseEntity.badRequest().body(null); */

        // Get the file's extension
        String fileName = file.getOriginalFilename();
        int extIdx = fileName.lastIndexOf(".");
        if (extIdx < 0)
            return ResponseEntity.badRequest().body(null);
        String fileExtension = fileName.substring(extIdx);
        if (fileExtension.length() < 2)
            return ResponseEntity.badRequest().body(null);

        // Enqueue the file
        String newFileName = queueService.enqueueFile(fileExtension, file.getInputStream());
        
        // Respond
        FileDataResponse response = new FileDataResponse();
        response.setFileName(newFileName);
        return ResponseEntity.ok().body(response);
    }

    @GetMapping("/status/{file}")
    public ResponseEntity<FileStatusResponse> getFileStatus(@PathVariable String file) {
        return null;
    }

    @GetMapping("/download/{file}")
    public ResponseEntity<Resource> downloadFile() {
        return null;
    }

}
