package org.doca.exception;

import org.springframework.http.HttpStatus;

/**
 * Exception for MCP-related errors
 */
public class MCPException extends RuntimeException {
    
    private final HttpStatus status;
    
    public MCPException(String message) {
        this(message, HttpStatus.BAD_REQUEST);
    }
    
    public MCPException(String message, HttpStatus status) {
        super(message);
        this.status = status;
    }
    
    public HttpStatus getStatus() {
        return status;
    }
}
