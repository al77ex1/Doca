package org.doca.dto.mapper;

import org.doca.dto.request.DocumentRequest;
import org.doca.dto.response.DocumentResponse;
import org.doca.entity.Document;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.factory.Mappers;

import java.util.List;

/**
 * Mapper for converting between Document entity and DTOs
 */
@Mapper(componentModel = "spring")
public interface DocumentMapper {
    
    DocumentMapper INSTANCE = Mappers.getMapper(DocumentMapper.class);
    
    /**
     * Convert entity to response DTO
     */
    DocumentResponse toResponse(Document document);
    
    /**
     * Convert list of entities to list of response DTOs
     */
    List<DocumentResponse> toResponseList(List<Document> documents);
    
    /**
     * Convert request DTO to entity
     */
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    Document toEntity(DocumentRequest request);
    
    /**
     * Update entity from request DTO
     */
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    void updateEntityFromRequest(DocumentRequest request, @MappingTarget Document document);
}
