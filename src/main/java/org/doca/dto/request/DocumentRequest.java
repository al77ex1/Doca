package org.doca.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.util.Base64;

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
    
    /**
     * Sets file content from a Base64-encoded string
     * @param content Base64-encoded string
     */
    @JsonProperty("fileContent")
    public void setFileContentFromBase64(String content) {
        if (content != null && !content.isEmpty()) {
            this.fileContent = Base64.getDecoder().decode(content);
        }
    }
    
    /**
     * Gets file content as a Base64-encoded string
     * @return Base64-encoded string representation of file content
     */
    @JsonProperty("fileContent")
    public String getFileContentAsBase64() {
        if (fileContent != null) {
            return Base64.getEncoder().encodeToString(fileContent);
        }
        return null;
    }
}
