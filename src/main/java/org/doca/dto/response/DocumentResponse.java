package org.doca.dto.response;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Response DTO for Document operations
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DocumentResponse {
    
    private Long id;
    private String filename;
    private String filetype;
    private LocalDateTime uploadedAt;
    private String extractedText;
}
