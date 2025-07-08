package org.doca.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Response DTO for MCP list resources operation
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MCPListResourcesResponse {
    
    private String status;
    private String nextCursor;
    private List<MCPResourceItem> resources;
    
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MCPResourceItem {
        private String uri;
        private String name;
        private String type;
        private String timestamp;
    }
}
