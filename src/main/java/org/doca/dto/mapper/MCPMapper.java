package org.doca.dto.mapper;

import org.doca.dto.response.MCPListResourcesResponse;
import org.doca.dto.response.MCPResourceResponse;
import org.doca.entity.Document;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * Mapper for MCP DTOs
 */
@Component
public class MCPMapper {

    /**
     * Convert a page of documents to MCPListResourcesResponse
     * 
     * @param documents Page of documents
     * @param nextPage Next page number or null if no next page
     * @return MCPListResourcesResponse
     */
    public MCPListResourcesResponse toListResourcesResponse(Page<Document> documents, Integer nextPage) {
        List<MCPListResourcesResponse.MCPResourceItem> resources = new ArrayList<>();
        
        for (Document doc : documents.getContent()) {
            resources.add(MCPListResourcesResponse.MCPResourceItem.builder()
                    .uri("doc:" + doc.getId())
                    .name(doc.getFilename())
                    .type(doc.getFiletype())
                    .timestamp(doc.getUploadedAt().toString())
                    .build());
        }
        
        return MCPListResourcesResponse.builder()
                .status("success")
                .nextCursor(nextPage != null ? nextPage.toString() : null)
                .resources(resources)
                .build();
    }
    
    /**
     * Convert a document to MCPResourceResponse
     * 
     * @param document Document entity
     * @return MCPResourceResponse
     */
    public MCPResourceResponse toResourceResponse(Document document) {
        if (document == null) {
            return MCPResourceResponse.builder()
                    .status("error")
                    .message("Resource not found")
                    .build();
        }
        
        MCPResourceResponse.ResourceContent content = MCPResourceResponse.ResourceContent.builder()
                .uri("doc:" + document.getId())
                .name(document.getFilename())
                .type(document.getFiletype())
                .timestamp(document.getUploadedAt().toString())
                .build();
        
        // Add extracted text if available
        if (document.getExtractedText() != null && !document.getExtractedText().isEmpty()) {
            content.setText(document.getExtractedText());
        }
        
        return MCPResourceResponse.builder()
                .status("success")
                .content(content)
                .build();
    }
    
    /**
     * Create an error response
     * 
     * @param message Error message
     * @return MCPResourceResponse with error
     */
    public MCPResourceResponse toErrorResponse(String message) {
        return MCPResourceResponse.builder()
                .status("error")
                .message(message)
                .build();
    }
}
