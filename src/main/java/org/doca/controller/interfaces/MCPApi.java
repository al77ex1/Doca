package org.doca.controller.interfaces;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.doca.dto.request.JsonRpcRequest;
import org.doca.dto.response.MCPUnifiedResponse;
import org.doca.interceptor.ErrorMessage;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;

/**
 * Unified API interface for MCP (Model Control Protocol)
 * Provides a single entry point for AI clients using JSON-RPC 2.0 format
 */
@Tag(name = "MCP", description = "Single entry point for Model Control Protocol operations")
@RequestMapping("/mcp")
public interface MCPApi {

    @PostMapping
    @Operation(
        summary = "MCP endpoint",
        description = "Single entry point for all MCP operations using JSON-RPC 2.0 format. Operations are determined by the 'method' field in the request body."
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
            @RequestBody JsonRpcRequest request);
}
