package com.kpuig.datasetserver.entity;

import java.io.Serializable;

public class VideoDataId implements Serializable {
    private Long vIndex;

    private Long setDataId;

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

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((vIndex == null) ? 0 : vIndex.hashCode());
        result = prime * result + ((setDataId == null) ? 0 : setDataId.hashCode());
        return result;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        VideoDataId other = (VideoDataId) obj;
        if (vIndex == null) {
            if (other.vIndex != null)
                return false;
        } else if (!vIndex.equals(other.vIndex))
            return false;
        if (setDataId == null) {
            if (other.setDataId != null)
                return false;
        } else if (!setDataId.equals(other.setDataId))
            return false;
        return true;
    }
}
