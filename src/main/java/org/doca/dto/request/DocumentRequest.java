package org.doca.dto.request;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

/**
 * Request DTO for Document operations
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DocumentRequest {
    
    @NotBlank(message = "Filename is required")
    @Size(min = 1, max = 255, message = "Filename must be between 1 and 255 characters")
    private String filename;
    
    @NotBlank(message = "Filetype is required")
    private String filetype;
    
    @NotNull(message = "File content is required")
    private byte[] fileContent;
}
