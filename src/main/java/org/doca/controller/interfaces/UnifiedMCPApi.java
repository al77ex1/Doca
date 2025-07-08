package org.doca.controller.interfaces;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.doca.dto.response.MCPUnifiedResponse;
import org.doca.interceptor.ErrorMessage;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * Unified API interface for MCP (Model Control Protocol)
 * Provides a single entry point for AI clients
 */
@Tag(name = "Unified MCP", description = "Single entry point for Model Control Protocol operations")
@RequestMapping("/mcp")
public interface UnifiedMCPApi {

    @PostMapping
    @Operation(
        summary = "Unified MCP endpoint",
        description = "Single entry point for all MCP operations. Operations are determined by the 'type' parameter."
    )
    @ApiResponse(
        responseCode = "200", 
        description = "Operation completed successfully",
        content = @Content(schema = @Schema(implementation = MCPUnifiedResponse.class))
    )
    @ApiResponse(
        responseCode = "400", 
        description = "Invalid request",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "404", 
        description = "Resource not found",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "500", 
        description = "Server error",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    ResponseEntity<MCPUnifiedResponse> processRequest(
            @Parameter(description = "Operation type (list_resources, read_resource, server_info)", required = true) 
            @RequestParam String type,
            
            @Parameter(description = "Resource URI (required for read_resource)") 
            @RequestParam(required = false) String uri,
            
            @Parameter(description = "Pagination cursor (optional for list_resources)") 
            @RequestParam(required = false) String cursor);
}
