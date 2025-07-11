package org.doca.dto.request;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Represents a JSON-RPC 2.0 request
 * Example:
 * {
 *   "jsonrpc": "2.0",
 *   "method": "server_info",
 *   "params": {},
 *   "id": 1
 * }
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class JsonRpcRequest {
    
    @JsonProperty("jsonrpc")
    private String jsonrpc;
    
    @JsonProperty("method")
    private String method;
    
    @JsonProperty("params")
    private Map<String, Object> params;
    
    @JsonProperty("id")
    private Object id;
    
    /**
     * Validates if this is a valid JSON-RPC 2.0 request
     * @return true if valid, false otherwise
     */
    public boolean isValid() {
        return "2.0".equals(jsonrpc) && method != null && !method.isEmpty();
    }
    
    /**
     * Gets a parameter value as a string
     * @param name parameter name
     * @return parameter value as string or null if not found
     */
    public String getStringParam(String name) {
        if (params == null || !params.containsKey(name)) {
            return null;
        }
        Object value = params.get(name);
        return value != null ? value.toString() : null;
    }
}
