package org.doca.controller;

import io.swagger.v3.oas.annotations.tags.Tag;
import org.doca.controller.interfaces.UnifiedMCPApi;
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
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Arrays;

/**
 * Unified controller for MCP (Model Control Protocol) operations
 * Provides a single entry point for AI clients
 */
@RestController
@Tag(name = "Unified MCP", description = "Single entry point for Model Control Protocol operations")
public class UnifiedMCPController implements UnifiedMCPApi {

    private static final Logger logger = LoggerFactory.getLogger(UnifiedMCPController.class);
    private final MCPService mcpService;
    
    @Value("${mcp.server.name:DocaStore}")
    private String serverName;

    @Autowired
    public UnifiedMCPController(MCPService mcpService) {
        this.mcpService = mcpService;
    }

    @Override
    public ResponseEntity<MCPUnifiedResponse> processRequest(
            @RequestParam String type, 
            @RequestParam(required = false) String uri, 
            @RequestParam(required = false) String cursor) {
        
        logger.debug("Processing MCP request of type: {}", type);
        
        if (type == null || type.isEmpty()) {
            throw new MCPException("Missing required parameter: type");
        }
        
        switch (type) {
            case "list_resources":
                return handleListResources(cursor);
                
            case "read_resource":
                return handleReadResource(uri);
                
            case "server_info":
                return handleServerInfo();
                
            default:
                throw new MCPException("Unsupported operation type: " + type);
        }
    }
    
    private ResponseEntity<MCPUnifiedResponse> handleListResources(String cursor) {
        MCPListResourcesResponse listResponse = mcpService.listResources(cursor);
        
        MCPUnifiedResponse response = MCPUnifiedResponse.builder()
                .status(listResponse.getStatus())
                .nextCursor(listResponse.getNextCursor())
                .resources(listResponse.getResources())
                .build();
                
        return ResponseEntity.ok(response);
    }
    
    private ResponseEntity<MCPUnifiedResponse> handleReadResource(String uri) {
        if (uri == null || uri.isEmpty()) {
            throw new MCPException("Missing required parameter: uri");
        }
        
        MCPResourceResponse resourceResponse = mcpService.readResource(uri);
        
        if ("error".equals(resourceResponse.getStatus()) && 
            resourceResponse.getMessage() != null && 
            resourceResponse.getMessage().contains("not found")) {
            throw new MCPException("Resource not found: " + uri, HttpStatus.NOT_FOUND);
        }
        
        MCPUnifiedResponse response = MCPUnifiedResponse.builder()
                .status(resourceResponse.getStatus())
                .message(resourceResponse.getMessage())
                .content(resourceResponse.getContent())
                .build();
                
        return ResponseEntity.ok(response);
    }
    
    private ResponseEntity<MCPUnifiedResponse> handleServerInfo() {
        String[] operations = {"list_resources", "read_resource", "server_info"};
        
        MCPUnifiedResponse response = MCPUnifiedResponse.builder()
                .status("success")
                .serverName(serverName)
                .version("1.0.0")
                .supportedOperations(Arrays.asList(operations))
                .build();
                
        return ResponseEntity.ok(response);
    }
}
