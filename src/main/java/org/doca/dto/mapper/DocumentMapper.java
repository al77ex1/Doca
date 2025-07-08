package org.doca.dto.mapper;

import org.doca.dto.request.DocumentRequest;
import org.doca.dto.response.DocumentResponse;
import org.doca.entity.Document;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.springframework.stereotype.Component;

/**
 * Mapper for converting between Document entity and DTOs
 */
@Mapper(componentModel = "spring")
@Component
public interface DocumentMapper {
    
    /**
     * Convert entity to response DTO
     */
    DocumentResponse toResponse(Document document);
    
    /**
     * Convert request DTO to entity
     */
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "uploadedAt", ignore = true)
    @Mapping(target = "extractedText", ignore = true)
    Document toEntity(DocumentRequest request);
}
