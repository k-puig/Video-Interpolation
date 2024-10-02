package com.kpuig.datasetserver.repo;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import com.kpuig.datasetserver.entity.VideoData;
import com.kpuig.datasetserver.entity.VideoDataId;

@Repository
public interface VideoDataRepository extends JpaRepository<VideoData, VideoDataId> {
    @Modifying
    @Transactional
    @Query("UPDATE VideoData e SET e.vIndex = ?2 WHERE e.vIndex = ?1")
    int updateIndexByNewIndex(Long vIndex, Long newIndex);

    @Modifying
    @Transactional
    @Query("UPDATE VideoData e SET e.frameCount = ?2 WHERE e.vIndex = ?1")
    int updateFrameCountByIndex(Long vIndex, Long frameCount);

    List<VideoData> findAllBySetDataId(Long setDataId);
    Long countBySetDataId(Long setDataId);
}
