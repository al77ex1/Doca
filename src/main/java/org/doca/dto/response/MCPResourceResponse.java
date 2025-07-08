package org.doca.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Response DTO for MCP read resource operation
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MCPResourceResponse {
    
    private String status;
    private String message;
    private ResourceContent content;
    
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ResourceContent {
        private String uri;
        private String name;
        private String type;
        private String timestamp;
        private String text;
    }
}
