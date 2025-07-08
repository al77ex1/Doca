package org.doca.service;

import org.doca.dto.mapper.MCPMapper;
import org.doca.dto.response.MCPListResourcesResponse;
import org.doca.dto.response.MCPResourceResponse;
import org.doca.entity.Document;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.Optional;

/**
 * Service for handling MCP (Model Control Protocol) operations
 */
@Service
public class MCPService {

    private static final int DEFAULT_PAGE_SIZE = 20;
    private final DocumentService documentService;
    private final MCPMapper mcpMapper;

    @Autowired
    public MCPService(DocumentService documentService, MCPMapper mcpMapper) {
        this.documentService = documentService;
        this.mcpMapper = mcpMapper;
    }

    /**
     * List available resources with pagination
     * 
     * @param cursor Pagination cursor (can be null for first page)
     * @return MCPListResourcesResponse containing resources and pagination info
     */
    public MCPListResourcesResponse listResources(String cursor) {
        int page = 0;
        if (cursor != null && !cursor.isEmpty()) {
            try {
                page = Integer.parseInt(cursor);
            } catch (NumberFormatException e) {
                // Default to first page if cursor is invalid
            }
        }

        Pageable pageable = PageRequest.of(page, DEFAULT_PAGE_SIZE);
        Page<Document> documents = documentService.getAllDocuments(pageable);
        
        Integer nextPage = null;
        if (documents.hasNext()) {
            nextPage = page + 1;
        }
        
        return mcpMapper.toListResourcesResponse(documents, nextPage);
    }

    /**
     * Read a specific resource by URI
     * 
     * @param uri Resource URI (format: doc:{id})
     * @return MCPResourceResponse containing resource data
     */
    public MCPResourceResponse readResource(String uri) {
        if (uri == null || !uri.startsWith("doc:")) {
            return mcpMapper.toErrorResponse("Invalid URI format. Expected format: doc:{id}");
        }
        
        try {
            String idStr = uri.substring(4); // Remove "doc:" prefix
            Long id = Long.parseLong(idStr);
            
            Optional<Document> documentOpt = documentService.getDocumentById(id);
            if (documentOpt.isPresent()) {
                return mcpMapper.toResourceResponse(documentOpt.get());
            } else {
                return mcpMapper.toErrorResponse("Resource not found: " + uri);
            }
        } catch (NumberFormatException e) {
            return mcpMapper.toErrorResponse("Invalid document ID in URI: " + uri);
        } catch (Exception e) {
            return mcpMapper.toErrorResponse("Error reading resource: " + e.getMessage());
        }
    }
}
