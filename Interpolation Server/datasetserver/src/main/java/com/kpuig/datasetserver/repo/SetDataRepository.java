package com.kpuig.datasetserver.repo;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import com.kpuig.datasetserver.entity.SetData;

@Repository
public interface SetDataRepository extends JpaRepository<SetData, Long> {
    public Optional<SetData> findByType(String type);

    @Modifying
    @Transactional
    @Query("UPDATE SetData e SET e.totalFrameCount = ?2 WHERE e.type = ?1")
    int updateTotalFrameCountByType(String type, Long totalFrameCount);
}
