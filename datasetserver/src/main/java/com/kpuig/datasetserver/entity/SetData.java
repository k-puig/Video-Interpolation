package com.kpuig.datasetserver.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class SetData {
    @Id
    @GeneratedValue(strategy=GenerationType.SEQUENCE)
    private Long id;

    @Column(length = 10)
    private String type;

    private Long totalFrameCount;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public Long getTotalFrameCount() {
        return totalFrameCount;
    }

    public void setTotalFrameCount(Long totalFrameCount) {
        this.totalFrameCount = totalFrameCount;
    }
}
