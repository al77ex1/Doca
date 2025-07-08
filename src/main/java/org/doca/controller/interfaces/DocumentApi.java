package org.doca.controller.interfaces;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.doca.dto.request.DocumentRequest;
import org.doca.dto.response.DocumentResponse;
import org.doca.interceptor.ErrorMessage;
import org.springframework.data.domain.Pageable;
import org.springframework.hateoas.EntityModel;
import org.springframework.hateoas.PagedModel;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;

@Tag(name = "Documents", description = "Operations related to document management")
@RequestMapping("/api/documents")
public interface DocumentApi {

    @GetMapping
    @Operation(
        summary = "Get documents",
        description = "Retrieves a paginated list of documents with sorting options"
    )
    @ApiResponse(
        responseCode = "200", 
        description = "Documents retrieved successfully",
        content = @Content(schema = @Schema(implementation = DocumentResponse.class))
    )
    @ApiResponse(
        responseCode = "400", 
        description = "Invalid request",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "401", 
        description = "Unauthorized access",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "403", 
        description = "Forbidden access",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "500", 
        description = "Server error",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    ResponseEntity<PagedModel<EntityModel<DocumentResponse>>> getAllDocuments(Pageable pageable);
    
    @GetMapping("/{id}")
    @Operation(
        summary = "Get document by ID",
        description = "Retrieves a specific document by its ID"
    )
    @ApiResponse(
        responseCode = "200", 
        description = "Document retrieved successfully",
        content = @Content(schema = @Schema(implementation = DocumentResponse.class))
    )
    @ApiResponse(
        responseCode = "400", 
        description = "Invalid request",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "401", 
        description = "Unauthorized access",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "403", 
        description = "Forbidden access",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "404", 
        description = "Document not found",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "500", 
        description = "Server error",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    ResponseEntity<DocumentResponse> getDocumentById(
        @Parameter(description = "Document ID") @PathVariable Long id
    );
    
    @PostMapping
    @Operation(
        summary = "Create a new document",
        description = "Creates a new document with the provided details"
    )
    @ApiResponse(
        responseCode = "201", 
        description = "Document created successfully",
        content = @Content(schema = @Schema(implementation = DocumentResponse.class))
    )
    @ApiResponse(
        responseCode = "400", 
        description = "Invalid request",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "401", 
        description = "Unauthorized access",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "403", 
        description = "Forbidden access",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "500", 
        description = "Server error",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    ResponseEntity<DocumentResponse> createDocument(
        @Parameter(description = "Document details") @Valid @RequestBody DocumentRequest request
    );
    
    @PutMapping("/{id}")
    @Operation(
        summary = "Update document",
        description = "Updates an existing document with the provided details"
    )
    @ApiResponse(
        responseCode = "200", 
        description = "Document updated successfully",
        content = @Content(schema = @Schema(implementation = DocumentResponse.class))
    )
    @ApiResponse(
        responseCode = "400", 
        description = "Invalid request",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "401", 
        description = "Unauthorized access",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "403", 
        description = "Forbidden access",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "404", 
        description = "Document not found",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "500", 
        description = "Server error",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    ResponseEntity<DocumentResponse> updateDocument(
        @Parameter(description = "Document ID") @PathVariable Long id,
        @Parameter(description = "Updated document details") @Valid @RequestBody DocumentRequest request
    );
    
    @DeleteMapping("/{id}")
    @Operation(
        summary = "Delete document",
        description = "Deletes a document by its ID"
    )
    @ApiResponse(
        responseCode = "204", 
        description = "Document deleted successfully"
    )
    @ApiResponse(
        responseCode = "400", 
        description = "Invalid request",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "401", 
        description = "Unauthorized access",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "403", 
        description = "Forbidden access",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "404", 
        description = "Document not found",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    @ApiResponse(
        responseCode = "500", 
        description = "Server error",
        content = @Content(schema = @Schema(implementation = ErrorMessage.class))
    )
    ResponseEntity<Void> deleteDocument(
        @Parameter(description = "Document ID") @PathVariable Long id
    );
}
