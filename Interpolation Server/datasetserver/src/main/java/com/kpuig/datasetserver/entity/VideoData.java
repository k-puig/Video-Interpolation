package com.kpuig.datasetserver.entity;

import org.springframework.data.domain.Persistable;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.Transient;

@Entity
@IdClass(VideoDataId.class)
public class VideoData implements Persistable<VideoDataId> {
    @Transient
    private static boolean initializing = true;

    @Id
    private Long vIndex;

    @Id
    private Long setDataId;

    private Long totalIndex;

    private Long frameCount;

    private String fileName;

    public Long getvIndex() {
        return vIndex;
    }

    public void setvIndex(Long id) {
        this.vIndex = id;
    }

    public Long getSetDataId() {
        return setDataId;
    }

    public void setSetDataId(Long setDataId) {
        this.setDataId = setDataId;
    }

    public Long getTotalIndex() {
        return totalIndex;
    }

    public void setTotalIndex(Long totalIndex) {
        this.totalIndex = totalIndex;
    }

    public Long getFrameCount() {
        return frameCount;
    }

    public void setFrameCount(Long frameCount) {
        this.frameCount = frameCount;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    @Override
    public VideoDataId getId() {
        VideoDataId id = new VideoDataId();
        id.setSetDataId(setDataId);
        id.setvIndex(vIndex);
        return id;
    }

    @Override
    public boolean isNew() {
        return initializing;
    }

    public static void endInitialization() {
        initializing = false;
    }
}
