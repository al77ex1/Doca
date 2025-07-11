package org.doca.service;

import org.doca.entity.Document;
import org.doca.repository.DocumentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Optional;

@Service
public class DocumentService {
    
    private final DocumentRepository documentRepository;
    
    @Autowired
    public DocumentService(DocumentRepository documentRepository) {
        this.documentRepository = documentRepository;
    }
    
    /**
     * Get all documents with pagination support
     * @param pageable Pagination information
     * @return Page of documents
     */
    public Page<Document> getAllDocuments(Pageable pageable) {
        return documentRepository.findAll(pageable);
    }
    
    public Optional<Document> getDocumentById(Long id) {
        return documentRepository.findById(id);
    }
    
    @Transactional
    public Document createDocument(Document document) {
        document.setUploadedAt(LocalDateTime.now());
        return documentRepository.save(document);
    }
    
    @Transactional
    public Optional<Document> updateDocument(Long id, Document updatedDocument) {
        return documentRepository.findById(id)
                .map(existingDocument -> {
                    existingDocument.setFilename(updatedDocument.getFilename());
                    existingDocument.setFiletype(updatedDocument.getFiletype());
                    existingDocument.setExtractedText(updatedDocument.getExtractedText());
                    // Don't update file content and upload date
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
