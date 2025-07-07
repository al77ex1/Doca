package org.doca.controller.interfaces;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.doca.entity.Document;
import org.doca.interceptor.ErrorMessage;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.List;

@Tag(name = "Documents", description = "Operations related to document management")
@RequestMapping("/api/documents")
public interface DocumentApi {

    @GetMapping
    @Operation(
        summary = "Get all documents",
        description = "Retrieves a list of all available documents"
    )
    @ApiResponse(
        responseCode = "200", 
        description = "Documents retrieved successfully",
        content = @Content(schema = @Schema(implementation = Document.class))
    )
    @ApiResponse(
        responseCode = "500", 
        description = "Server error",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    ResponseEntity<List<Document>> getAllDocuments();
}
