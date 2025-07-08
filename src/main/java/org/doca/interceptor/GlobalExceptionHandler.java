package org.doca.interceptor;

import org.doca.exception.MCPException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

/**
 * Global exception handler for API errors
 */
@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MCPException.class)
    public ResponseEntity<ErrorMessage> handleMCPException(MCPException ex) {
        ErrorMessage errorMessage = new ErrorMessage(
                ex.getStatus().value(),
                ex.getMessage()
        );
        return new ResponseEntity<>(errorMessage, ex.getStatus());
    }
    
    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<ErrorMessage> handleMissingParams(MissingServletRequestParameterException ex) {
        String paramName = ex.getParameterName();
        ErrorMessage errorMessage = new ErrorMessage(
                400,
                "Missing required parameter: " + paramName
        );
        return ResponseEntity.badRequest().body(errorMessage);
    }
    
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<ErrorMessage> handleTypeMismatch(MethodArgumentTypeMismatchException ex) {
        String paramName = ex.getName();
        ErrorMessage errorMessage = new ErrorMessage(
                400,
                "Invalid value for parameter: " + paramName
        );
        return ResponseEntity.badRequest().body(errorMessage);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorMessage> handleGenericException(Exception ex) {
        ErrorMessage errorMessage = new ErrorMessage(
                500,
                "Internal server error: " + ex.getMessage()
        );
        return ResponseEntity.internalServerError().body(errorMessage);
    }
}
