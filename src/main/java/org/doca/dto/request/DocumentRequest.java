package org.doca.dto.request;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Request DTO for Document operations
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DocumentRequest {
    
    @NotBlank(message = "Document name is required")
    @Size(min = 3, max = 255, message = "Document name must be between 3 and 255 characters")
    private String name;
}
