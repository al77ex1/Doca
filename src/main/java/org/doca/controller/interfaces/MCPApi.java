package org.doca.controller.interfaces;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.doca.dto.response.MCPListResourcesResponse;
import org.doca.dto.response.MCPResourceResponse;
import org.doca.interceptor.ErrorMessage;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Tag(name = "MCP", description = "Model Control Protocol endpoints")
@RequestMapping("/mcp")
public interface MCPApi {

    @GetMapping("/resources")
    @Operation(
        summary = "List available resources",
        description = "Lists all available document resources with pagination"
    )
    @ApiResponse(
        responseCode = "200", 
        description = "Resources listed successfully",
        content = @Content(schema = @Schema(implementation = MCPListResourcesResponse.class))
    )
    @ApiResponse(
        responseCode = "400", 
        description = "Invalid request",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "500", 
        description = "Server error",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    ResponseEntity<MCPListResourcesResponse> listResources(
            @Parameter(description = "Pagination cursor") 
            @RequestParam(required = false) String cursor);

    @GetMapping("/resources/{uri}")
    @Operation(
        summary = "Read resource",
        description = "Reads a specific resource by its URI"
    )
    @ApiResponse(
        responseCode = "200", 
        description = "Resource read successfully",
        content = @Content(schema = @Schema(implementation = MCPResourceResponse.class))
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
    ResponseEntity<MCPResourceResponse> readResource(
            @Parameter(description = "Resource URI", example = "doc:123") 
            @PathVariable String uri);
}
