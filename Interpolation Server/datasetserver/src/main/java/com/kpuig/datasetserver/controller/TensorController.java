package com.kpuig.datasetserver.controller;

import java.awt.Point;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import com.kpuig.datasetserver.service.TensorService;

@RestController
public class TensorController {
    @Autowired
    private TensorService service;
    
    @GetMapping("/{set}/video_count")
    public ResponseEntity<Long> getVideoCount(@PathVariable("set") String set) {
        Long videoCount = service.getVideoCount(set);
        if (videoCount <= 0) {
            return ResponseEntity.internalServerError().body(videoCount);
        }
        return ResponseEntity.ok(videoCount);
    }

    @GetMapping("/{set}/total_frame_count")
    public ResponseEntity<Long> getTotalFrameCount(@PathVariable("set") String set) {
        Long frameCount = service.getTotalFrameCount(set);
        if (frameCount <= 0) {
            return ResponseEntity.internalServerError().body(frameCount);
        }
        return ResponseEntity.ok(frameCount);
    }

    @GetMapping("/{set}/{total_index}/tensor")
    public ResponseEntity<ByteArrayResource> getTensorByTotalIndex(@PathVariable("set") String set, @PathVariable("total_index") long totalIndex) {
        byte[] tensor = service.getTensorByTotalIndex(set, totalIndex);
        if (tensor == null || tensor.length < 8) {
            return ResponseEntity.internalServerError().body(null);
        }
        ByteArrayResource dataResource = new ByteArrayResource(tensor);
        HttpHeaders headers = new HttpHeaders();
        headers.add(HttpHeaders.CONTENT_TYPE, "application/octet-stream");
        headers.add(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=tensor.bin");
        return new ResponseEntity<ByteArrayResource>(dataResource, headers, HttpStatus.OK);
    }
    

    @GetMapping("/{set}/{video_index}/frame_count")
    public ResponseEntity<Long> getFrameCount(@PathVariable("set") String set, @PathVariable("video_index") long videoIndex) {
        Long frameCount = service.getFrameCount(set, videoIndex);
        if (frameCount <= 0) {
            return ResponseEntity.internalServerError().body(frameCount);
        }
        return ResponseEntity.ok(frameCount);
    }

    @GetMapping("/{set}/{video_index}/{frame_index}/size")
    public ResponseEntity<String> getTensorSize(@PathVariable("set") String set, @PathVariable("video_index") long videoIndex, @PathVariable("frame_index") long frameIndex) {
        Point size = service.getTensorSize(set, videoIndex, frameIndex);
        if (size == null) {
            return ResponseEntity.internalServerError().body(null);
        }
        String sizeStr = size.x + "," + size.y;
        return ResponseEntity.ok().body(sizeStr);
    }

    @GetMapping("/{set}/{video_index}/{frame_index}/tensor")
    public ResponseEntity<ByteArrayResource> getTensor(@PathVariable("set") String set, @PathVariable("video_index") long videoIndex, @PathVariable("frame_index") long frameIndex) {
        byte[] tensor = service.getTensor(set, videoIndex, frameIndex);
        if (tensor == null || tensor.length < 8) {
            return ResponseEntity.internalServerError().body(null);
        }
        ByteArrayResource dataResource = new ByteArrayResource(tensor);
        HttpHeaders headers = new HttpHeaders();
        headers.add(HttpHeaders.CONTENT_TYPE, "application/octet-stream");
        headers.add(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=tensor.bin");
        return new ResponseEntity<ByteArrayResource>(dataResource, headers, HttpStatus.OK);
    }

}
