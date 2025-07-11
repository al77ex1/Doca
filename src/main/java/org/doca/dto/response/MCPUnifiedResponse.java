package org.doca.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * Unified response DTO for MCP operations with JSON-RPC 2.0 format
 * Example:
 * {
 *   "jsonrpc": "2.0",
 *   "result": { ... },
 *   "id": 1
 * }
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class MCPUnifiedResponse {
    
    // JSON-RPC 2.0 fields
    @JsonProperty("jsonrpc")
    private String jsonrpc;
    
    @JsonProperty("id")
    private Object id;
    
    @JsonProperty("error")
    private Map<String, Object> error;
    
    @JsonProperty("result")
    private Map<String, Object> result;
    
    // Legacy fields - will be mapped to result or error
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
