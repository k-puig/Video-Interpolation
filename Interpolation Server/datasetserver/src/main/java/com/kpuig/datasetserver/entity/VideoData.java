package com.kpuig.datasetserver.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;

@Entity
@IdClass(VideoDataId.class)
public class VideoData {
    @Id
    private Long vIndex;

    @Id
    private Long setDataId;

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
}
