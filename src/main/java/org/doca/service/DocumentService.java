package org.doca.service;

import org.doca.entity.Document;
import org.doca.repository.DocumentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class DocumentService {
    
    private final DocumentRepository documentRepository;
    
    @Autowired
    public DocumentService(DocumentRepository documentRepository) {
        this.documentRepository = documentRepository;
    }
    
    public List<Document> getAllDocuments() {
        return documentRepository.findAll();
    }
    
    public Optional<Document> getDocumentById(Long id) {
        return documentRepository.findById(id);
    }
    
    @Transactional
    public Document createDocument(Document document) {
        document.setCreatedAt(LocalDateTime.now());
        return documentRepository.save(document);
    }
    
    @Transactional
    public Optional<Document> updateDocument(Long id, Document updatedDocument) {
        return documentRepository.findById(id)
                .map(existingDocument -> {
                    existingDocument.setName(updatedDocument.getName());
                    // Keep the original creation date
                    return documentRepository.save(existingDocument);
                });
    }
    
    @Transactional
    public boolean deleteDocument(Long id) {
        return documentRepository.findById(id)
                .map(document -> {
                    documentRepository.delete(document);
                    return true;
                })
                .orElse(false);
    }
}
