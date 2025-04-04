package net.kpuig.nnqueue.controller;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import net.kpuig.nnqueue.controller.response.FileDataResponse;
import net.kpuig.nnqueue.controller.response.FileStatusResponse;
import net.kpuig.nnqueue.service.FileHandlingService;
import net.kpuig.nnqueue.service.data.FileStatus;

import java.io.IOException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;


@RestController
@RequestMapping("/queue")
public class QueueController {
    @Autowired private FileHandlingService queueService;

    @PostMapping("/upload")
    public ResponseEntity<FileDataResponse> uploadVideo(@RequestParam MultipartFile file) throws IOException {
        // Get the file's extension
        String fileName = file.getOriginalFilename();
        int extIdx = fileName.lastIndexOf(".");
        if (extIdx < 0)
            return ResponseEntity.badRequest().body(null);
        String fileExtension = fileName.substring(extIdx);
        if (fileExtension.length() < 2)
            return ResponseEntity.badRequest().body(null);

        // Enqueue the file
        String newFileName = queueService.enqueueFile(file.getInputStream());
        
        // Respond
        FileDataResponse response = new FileDataResponse();
        response.setFileName(newFileName);
        return ResponseEntity.ok().body(response);
    }

    @GetMapping("/status/{file}")
    public ResponseEntity<FileStatusResponse> getFileStatus(@PathVariable String file) {
        FileStatus status = queueService.getStatus(file);

        FileStatusResponse response = new FileStatusResponse();

        response.setStatus(status.toString());
        return ResponseEntity.ok().body(response);
    }

    @GetMapping("/download/{file}")
    public ResponseEntity<Resource> downloadFile(@PathVariable String file) {
        Resource resource = queueService.getDownloadableFileResource(file);
        if (resource == null)
            return ResponseEntity.badRequest().body(null);
        return ResponseEntity
                .ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + resource.getFilename() + "\"")
                .body(resource);
    }

}
