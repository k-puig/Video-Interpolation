package com.kpuig.datasetserver.service;

import java.io.File;

import org.bytedeco.javacv.FFmpegFrameGrabber;
import org.springframework.stereotype.Service;

@Service
public class FrameReaderService {
    public FFmpegFrameGrabber getFrameGrabber(File video) {
        FFmpegFrameGrabber grabber = new FFmpegFrameGrabber(video);
        return grabber;
    }
}