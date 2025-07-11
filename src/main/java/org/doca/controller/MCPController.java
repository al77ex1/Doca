package org.doca.controller;

import io.swagger.v3.oas.annotations.tags.Tag;
import org.doca.controller.interfaces.MCPApi;
import org.doca.dto.request.JsonRpcRequest;
import org.doca.dto.response.MCPListResourcesResponse;
import org.doca.dto.response.MCPResourceResponse;
import org.doca.dto.response.MCPUnifiedResponse;
import org.doca.exception.MCPException;
import org.doca.service.MCPService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * Unified controller for MCP (Model Control Protocol) operations
 * Provides a single entry point for AI clients using JSON-RPC 2.0 format
 */
@RestController
@Tag(name = "MCP", description = "Single entry point for Model Control Protocol operations")
public class MCPController implements MCPApi {

    private static final Logger logger = LoggerFactory.getLogger(MCPController.class);
    private final MCPService mcpService;
    
    @Value("${mcp.server.name:DocaStore}")
    private String serverName;

    @Autowired
    public MCPController(MCPService mcpService) {
        this.mcpService = mcpService;
    }

    @Override
    public ResponseEntity<MCPUnifiedResponse> processRequest(JsonRpcRequest request) {
        if (request == null || !request.isValid()) {
            throw new MCPException("Invalid JSON-RPC request format", HttpStatus.BAD_REQUEST);
        }
        
        String method = request.getMethod();
        logger.debug("Processing MCP JSON-RPC request for method: {}", method);
        
        MCPUnifiedResponse response;
        
        switch (method) {
            case "list_resources":
                response = handleListResources(request);
                break;
                
            case "read_resource":
                response = handleReadResource(request);
                break;
                
            case "server_info":
                response = handleServerInfo();
                break;
                
            default:
                throw new MCPException("Unsupported method: " + method, HttpStatus.BAD_REQUEST);
        }
        
        // Add JSON-RPC response fields
        response.setJsonrpc("2.0");
        
        // IMPORTANT: The id in the response MUST be exactly the same as the id in the request
        // This ensures proper request-response correlation, especially for parallel requests
        Object requestId = request.getId();
        if (requestId != null) {
            response.setId(requestId);
            logger.debug("Setting response id to match request id: {}", requestId);
        }
        
        return ResponseEntity.ok(response);
    }
    
    private MCPUnifiedResponse handleListResources(JsonRpcRequest request) {
        String cursor = request.getStringParam("cursor");
        MCPListResourcesResponse listResponse = mcpService.listResources(cursor);
        
        return MCPUnifiedResponse.builder()
                .status(listResponse.getStatus())
                .nextCursor(listResponse.getNextCursor())
                .resources(listResponse.getResources())
                .build();
    }
    
    private MCPUnifiedResponse handleReadResource(JsonRpcRequest request) {
        String uri = request.getStringParam("uri");
        
        if (uri == null || uri.isEmpty()) {
            throw new MCPException("Missing required parameter: uri", HttpStatus.BAD_REQUEST);
        }
        
        MCPResourceResponse resourceResponse = mcpService.readResource(uri);
        
        if ("error".equals(resourceResponse.getStatus()) && 
            resourceResponse.getMessage() != null && 
            resourceResponse.getMessage().contains("not found")) {
            throw new MCPException("Resource not found: " + uri, HttpStatus.NOT_FOUND);
        }
        
        return MCPUnifiedResponse.builder()
                .status(resourceResponse.getStatus())
                .message(resourceResponse.getMessage())
                .content(resourceResponse.getContent())
                .build();
    }
    
    private MCPUnifiedResponse handleServerInfo() {
        String[] operations = {"list_resources", "read_resource", "server_info"};
        
        Map<String, Object> result = new HashMap<>();
        result.put("serverName", serverName);
        result.put("version", "1.0.0");
        result.put("supportedOperations", Arrays.asList(operations));
        
        return MCPUnifiedResponse.builder()
                .status("success")
                .result(result)
                .build();
    }
}
