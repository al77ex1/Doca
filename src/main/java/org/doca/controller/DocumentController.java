package org.doca.controller;

import org.doca.controller.interfaces.DocumentApi;
import org.doca.dto.mapper.DocumentMapper;
import org.doca.dto.request.DocumentRequest;
import org.doca.dto.response.DocumentResponse;
import org.doca.entity.Document;
import org.doca.service.DocumentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PagedResourcesAssembler;
import org.springframework.hateoas.EntityModel;
import org.springframework.hateoas.PagedModel;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class DocumentController implements DocumentApi {
    
    private final DocumentService documentService;
    private final DocumentMapper documentMapper;
    private final PagedResourcesAssembler<Document> pagedResourcesAssembler;
    
    @Autowired
    public DocumentController(
            DocumentService documentService, 
            DocumentMapper documentMapper,
            PagedResourcesAssembler<Document> pagedResourcesAssembler) {
        this.documentService = documentService;
        this.documentMapper = documentMapper;
        this.pagedResourcesAssembler = pagedResourcesAssembler;
    }
    
    @Override
    public ResponseEntity<PagedModel<EntityModel<DocumentResponse>>> getAllDocuments(Pageable pageable) {
        Page<Document> documentPage = documentService.getAllDocuments(pageable);
        PagedModel<EntityModel<DocumentResponse>> pagedModel = pagedResourcesAssembler.toModel(
                documentPage,
                entity -> EntityModel.of(documentMapper.toResponse(entity))
        );
        return ResponseEntity.ok(pagedModel);
    }
    
    @Override
    public ResponseEntity<DocumentResponse> getDocumentById(Long id) {
        return documentService.getDocumentById(id)
                .map(document -> ResponseEntity.ok(documentMapper.toResponse(document)))
                .orElse(ResponseEntity.notFound().build());
    }
    
    @Override
    public ResponseEntity<DocumentResponse> createDocument(DocumentRequest request) {
        Document document = documentMapper.toEntity(request);
        Document savedDocument = documentService.createDocument(document);
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(documentMapper.toResponse(savedDocument));
    }
    
    @Override
    public ResponseEntity<DocumentResponse> updateDocument(Long id, DocumentRequest request) {
        Document documentToUpdate = documentMapper.toEntity(request);
        return documentService.updateDocument(id, documentToUpdate)
                .map(updatedDocument -> ResponseEntity.ok(documentMapper.toResponse(updatedDocument)))
                .orElse(ResponseEntity.notFound().build());
    }
    
    @Override
    public ResponseEntity<Void> deleteDocument(Long id) {
        boolean deleted = documentService.deleteDocument(id);
        if (deleted) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
