package org.doca.controller;

import org.doca.controller.interfaces.DocumentApi;
import org.doca.dto.mapper.DocumentMapper;
import org.doca.dto.request.DocumentRequest;
import org.doca.dto.response.DocumentResponse;
import org.doca.entity.Document;
import org.doca.service.DocumentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class DocumentController implements DocumentApi {
    
    private final DocumentService documentService;
    private final DocumentMapper documentMapper;
    
    @Autowired
    public DocumentController(DocumentService documentService, DocumentMapper documentMapper) {
        this.documentService = documentService;
        this.documentMapper = documentMapper;
    }
    
    @Override
    public ResponseEntity<List<DocumentResponse>> getAllDocuments() {
        List<Document> documents = documentService.getAllDocuments();
        List<DocumentResponse> responseList = documents.stream()
                .map(documentMapper::toResponse)
                .toList();
        return ResponseEntity.ok(responseList);
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
