package net.kpuig.nnqueue.controller.response;

import jakarta.validation.constraints.Pattern;
import lombok.Data;

@Data
public class FileStatusResponse {
    @Pattern(regexp = "queued|errored|processing|processed")
    private String status;
}
