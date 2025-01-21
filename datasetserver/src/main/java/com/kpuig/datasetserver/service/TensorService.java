package com.kpuig.datasetserver.service;

import java.awt.Point;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Optional;

import org.bytedeco.javacv.FFmpegFrameGrabber;
import org.bytedeco.javacv.Frame;
import org.bytedeco.javacv.Java2DFrameConverter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.kpuig.datasetserver.entity.SetData;
import com.kpuig.datasetserver.entity.VideoData;
import com.kpuig.datasetserver.entity.VideoDataId;
import com.kpuig.datasetserver.repo.SetDataRepository;
import com.kpuig.datasetserver.repo.VideoDataRepository;

import jakarta.annotation.PostConstruct;

@Service
public class TensorService {
    @Value("${dataset.location.train}")
    private String trainDirectory;

    @Value("${dataset.location.validate}")
    private String validateDirectory;

    @Value("${dataset.location.test}")
    private String testDirectory;

    private VideoDataRepository vidDataRepo;
    private SetDataRepository setDataRepo;

    private FrameReaderService frameService;

    public TensorService(@Autowired VideoDataRepository vidDataRepo, 
                         @Autowired SetDataRepository setDataRepo,
                         @Autowired FrameReaderService frameService) {
        this.vidDataRepo = vidDataRepo;
        this.setDataRepo = setDataRepo;
        this.frameService = frameService;
    }

    @PostConstruct
    public void initializeVideoData() throws Exception {
        File trainDir = new File(trainDirectory);
        File valDir = new File(validateDirectory);
        File testDir = new File(testDirectory);

        if (!trainDir.isDirectory() ||
            !valDir.isDirectory() ||
            !testDir.isDirectory()) {
            throw new Exception("Unable to initialize the video data");
        }

        SetData trainSetData = new SetData();
        trainSetData.setType("train");
        trainSetData.setTotalFrameCount(null);
        SetData savedTrainSetData = setDataRepo.save(trainSetData);

        SetData valSetData = new SetData();
        valSetData.setType("validate");
        valSetData.setTotalFrameCount(null);
        SetData savedValSetData = setDataRepo.save(valSetData);

        SetData testSetData = new SetData();
        testSetData.setType("test");
        testSetData.setTotalFrameCount(null);
        SetData savedTestSetData = setDataRepo.save(testSetData);
        setDataRepo.flush();

        ArrayList<VideoData> trainVidData = new ArrayList<>();
        long i = 0;
        for (File f : trainDir.listFiles()) {
            if (Files.probeContentType(f.toPath()).toLowerCase().contains("video")) {
                VideoData data = new VideoData();
                data.setFileName(f.getName());
                data.setFrameCount(null);
                data.setSetDataId(savedTrainSetData.getId());
                data.setvIndex(i++);
                trainVidData.add(data);
            }
        }

        ArrayList<VideoData> valVidData = new ArrayList<>();
        i = 0;
        for (File f : valDir.listFiles()) {
            if (Files.probeContentType(f.toPath()).toLowerCase().contains("video")) {
                VideoData data = new VideoData();
                data.setFileName(f.getName());
                data.setFrameCount(null);
                data.setSetDataId(savedValSetData.getId());
                data.setvIndex(i++);
                valVidData.add(data);
            }
        }

        ArrayList<VideoData> testVidData = new ArrayList<>();
        i = 0;
        for (File f : testDir.listFiles()) {
            if (Files.probeContentType(f.toPath()).toLowerCase().contains("video")) {
                VideoData data = new VideoData();
                data.setFileName(f.getName());
                data.setFrameCount(null);
                data.setSetDataId(savedTestSetData.getId());
                data.setvIndex(i++);
                testVidData.add(data);
            }
        }

        ArrayList<VideoData> allVidData = new ArrayList<>();
        allVidData.addAll(trainVidData);
        allVidData.addAll(valVidData);
        allVidData.addAll(testVidData);

        System.out.println("Pushing all preliminary video data to DB...");
        vidDataRepo.saveAll(allVidData);
        System.out.println("DB initialization complete!");
        vidDataRepo.flush();
        VideoData.endInitialization();
    }

    public Long getVideoCount(String set) {
        Optional<SetData> setData = setDataRepo.findByType(set);
        if (setData.isEmpty()) {
            return -1L;
        }

        return vidDataRepo.countBySetDataId(setData.get().getId());
    }

    @Transactional
    public Long getTotalFrameCount(String set) {
        Optional<SetData> setData = setDataRepo.findByType(set);
        if (setData.isEmpty()) {
            return -1L;
        }
        if (setData.get().getTotalFrameCount() != null) {
            return setData.get().getTotalFrameCount();
        }

        Long totalFrameCount = 0L;
        Long videoCount = getVideoCount(set);
        for (long i = 0L; i < videoCount; i++) {
            long frameCount = getFrameCount(set, i);
            VideoDataId vId = new VideoDataId();
            vId.setSetDataId(setDataRepo.findByType(set).get().getId());
            vId.setvIndex(i);
            vidDataRepo.updateTotalIndexById(vId.getvIndex(), vId.getSetDataId(), totalFrameCount);
            vidDataRepo.flush();
            totalFrameCount += frameCount;
        }
        setDataRepo.updateTotalFrameCountByType(set, totalFrameCount);
        setDataRepo.flush();
        return totalFrameCount;
    }


    public Long getFrameCount(String set, Long videoIndex) {
        String directory = setToDirectory(set);

        Optional<SetData> setData = setDataRepo.findByType(set);
        if (setData.isEmpty()) {
            return -1L;
        }

        if (videoIndex < 0L || videoIndex >= getVideoCount(set)) {
            return -1L;
        }

        Long setDataId = setData.get().getId();
        VideoDataId videoDataId = new VideoDataId();
        videoDataId.setvIndex(videoIndex);
        videoDataId.setSetDataId(setDataId);
        
        Optional<VideoData> videoData = vidDataRepo.findById(videoDataId);
        if (videoData.isEmpty()) {
            return -1L;
        }

        if (videoData.get().getFrameCount() == null) {
            try {
                Long frameCount = getFrameCountFromDirectory(directory + "/" + videoData.get().getFileName());
                vidDataRepo.updateFrameCountByIndex(videoIndex, frameCount);
                vidDataRepo.flush();
                return frameCount;
            } catch (IOException e) {
                e.printStackTrace();
                return -1L;
            }
        }

        return videoData.get().getFrameCount();
    }

    public Point getTensorSize(String set, Long videoIndex, long frameIndex) {
        Optional<SetData> setData = setDataRepo.findByType(set);
        if (setData.isEmpty()) {
            return null;
        }

        String directory = setToDirectory(set);

        VideoDataId videoDataId = new VideoDataId();
        videoDataId.setvIndex(videoIndex);
        videoDataId.setSetDataId(setData.get().getId());

        Optional<VideoData> videoData = vidDataRepo.findById(videoDataId);
        if (videoData.isEmpty()) {
            return null;
        }

        if (frameIndex < 0L || frameIndex >= getFrameCount(set, videoIndex)) {
            return null;
        }
        FFmpegFrameGrabber grabber = frameService.getFrameGrabber(new File(directory + "/" + videoData.get().getFileName()));
        try {
            grabber.start();
            grabber.setFrameNumber((int) frameIndex);
            
            Java2DFrameConverter conv = new Java2DFrameConverter();
            Frame frame = grabber.grabImage();
            BufferedImage img = conv.convert(frame);

            int width = img.getWidth();
            int height = img.getHeight();

            Point resolution = new Point(width, height);

            grabber.stop();
            conv.close();

            return resolution;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public byte[] getTensorByTotalIndex(String set, Long totalIndex) {
        if (totalIndex < 0L)
            return null;

        Long totalFrames = getTotalFrameCount(set);
        if (totalIndex >= totalFrames)
            return null;

        VideoData vidData = vidDataRepo.findFirstByTotalIndexLessThanEqualOrderByTotalIndexDesc(totalIndex);
        if (vidData == null)
            return null;
        SetData setData = setDataRepo.findById(vidData.getSetDataId()).get();
        return getTensor(setData.getType(), vidData.getvIndex(), totalIndex - vidData.getTotalIndex());
    }

    // Returns a byte array of the form {widthInt, heightInt, RGB (3-byte) pixels Y-dominant}
    public byte[] getTensor(String set, Long videoIndex, long frameIndex) {
        Optional<SetData> setData = setDataRepo.findByType(set);
        if (setData.isEmpty()) {
            return null;
        }

        String directory = setToDirectory(set);

        VideoDataId videoDataId = new VideoDataId();
        videoDataId.setvIndex(videoIndex);
        videoDataId.setSetDataId(setData.get().getId());

        Optional<VideoData> videoData = vidDataRepo.findById(videoDataId);
        if (videoData.isEmpty()) {
            return null;
        }

        if (frameIndex < 0L || frameIndex >= getFrameCount(set, videoIndex)) {
            return null;
        }
        FFmpegFrameGrabber grabber = frameService.getFrameGrabber(new File(directory + "/" + videoData.get().getFileName()));
        try {
            grabber.start();
            grabber.setFrameNumber((int) frameIndex);
            
            Java2DFrameConverter conv = new Java2DFrameConverter();
            Frame frame = grabber.grabImage();
            BufferedImage img = conv.convert(frame);

            int width = img.getWidth();
            int height = img.getHeight();
            ByteArrayBuilder rgbBytes = new ByteArrayBuilder();

            rgbBytes.add(intToBytes(width));
            rgbBytes.add(intToBytes(height));
            for (int y = 0; y < height; y++) {
                for (int x = 0; x < width; x++) {
                    int pixel = img.getRGB(x, y);
                    byte[] rgb = new byte[]{
                        (byte) ((pixel & 0x00FF0000) >> 16),
                        (byte) ((pixel & 0x0000FF00) >> 8),
                        (byte) (pixel & 0x000000FF)
                    };
                    rgbBytes.add(rgb);
                }
            }

            grabber.stop();
            conv.close();

            return rgbBytes.getArray();
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    private String setToDirectory(String set) {
        String directory = set;
        if (set.equals("train")) {
            directory = trainDirectory;
        }
        else if (set.equals("validate")) {
            directory = validateDirectory;
        }
        else if (set.equals("test")) {
            directory = testDirectory;
        }

        return directory;
    }

    private long getFrameCountFromDirectory(String directory) throws IOException {
        File vid = new File(directory);
        if (!vid.isFile()) {
            return -1L;
        }

        FFmpegFrameGrabber grabber = frameService.getFrameGrabber(vid);
        long frameCount = 0;
        try {
            grabber.start();
            while (grabber.hasVideo() && grabber.grabImage() != null) {
                frameCount++;
            }
            grabber.stop();
        } catch (Exception e) {
            return frameCount;
        } 
        return frameCount;
    }

    private static byte[] intToBytes(int x) {
        byte[] result = new byte[4];
        result[0] = (byte) ((x & (0xFF << 24)) >> 24);
        result[1] = (byte) ((x & (0xFF << 16)) >> 16);
        result[2] = (byte) ((x & (0xFF << 8)) >> 8);
        result[3] = (byte) (x & 0xFF);
        return result;
    }

    private class ByteArrayBuilder {
        private int size;
        private byte[] array;

        public ByteArrayBuilder() {
            size = 0;
            array = new byte[0];
        }

        public void add(byte b) {
            if (size == array.length) {
                doubleArray();
            }

            array[size] = b;

            size++;
        }

        public void add(byte[] bytes) {
            for (byte b : bytes) {
                add(b);
            }
        }

        // Note: returns clone of size `size`
        public byte[] getArray() {
            return Arrays.copyOf(array, size);
        }

        @SuppressWarnings("unused")
        public byte[] getUnderlyingArray() {
            return array;
        }

        @SuppressWarnings("unused")
        public int size() {
            return size;
        }

        private void doubleArray() {
            byte[] newArray = Arrays.copyOf(array, Math.min(Integer.MAX_VALUE, Math.max(1, array.length * 2)));
            array = newArray;
        }
    }
}
