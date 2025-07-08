package org.doca.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.doca.controller.interfaces.MCPApi;
import org.doca.dto.response.MCPListResourcesResponse;
import org.doca.dto.response.MCPResourceResponse;
import org.doca.service.MCPService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST controller for MCP (Model Control Protocol) operations
 */
@RestController
@RequestMapping("/mcp")
@Tag(name = "MCP", description = "Model Control Protocol endpoints")
public class MCPController implements MCPApi {

    private final MCPService mcpService;

    @Autowired
    public MCPController(MCPService mcpService) {
        this.mcpService = mcpService;
    }

    @GetMapping("/resources")
    @Operation(
        summary = "List available resources",
        description = "Lists all available document resources with pagination"
    )
    @ApiResponse(
        responseCode = "200",
        description = "Resources listed successfully"
    )
    @Override
    public ResponseEntity<MCPListResourcesResponse> listResources(
            @Parameter(description = "Pagination cursor") 
            @RequestParam(required = false) String cursor) {
        MCPListResourcesResponse response = mcpService.listResources(cursor);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/resources/{uri}")
    @Operation(
        summary = "Read resource",
        description = "Reads a specific resource by its URI"
    )
    @ApiResponse(
        responseCode = "200",
        description = "Resource read successfully",
        content = @Content(schema = @Schema(implementation = Object.class))
    )
    @ApiResponse(
        responseCode = "404",
        description = "Resource not found"
    )
    @Override
    public ResponseEntity<MCPResourceResponse> readResource(
            @Parameter(description = "Resource URI", example = "doc:123") 
            @PathVariable String uri) {
        MCPResourceResponse response = mcpService.readResource(uri);
        
        if ("error".equals(response.getStatus()) && 
            response.getMessage() != null && 
            response.getMessage().contains("not found")) {
            return ResponseEntity.notFound().build();
        }
        
        return ResponseEntity.ok(response);
    }
}
