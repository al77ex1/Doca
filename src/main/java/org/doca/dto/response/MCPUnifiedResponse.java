package org.doca.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Unified response DTO for MCP operations
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class MCPUnifiedResponse {
    
    private String status;
    private String message;
    
    // For server_info operation
    private String serverName;
    private String version;
    private List<String> supportedOperations;
    
    // For list_resources operation
    private String nextCursor;
    private List<MCPListResourcesResponse.MCPResourceItem> resources;
    
    // For read_resource operation
    private MCPResourceResponse.ResourceContent content;
}
