package org.doca.config;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.doca.dto.response.MCPListResourcesResponse;
import org.doca.dto.response.MCPResourceResponse;
import org.doca.service.MCPService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class MCPWebSocketHandler extends TextWebSocketHandler {
    
    private static final Logger logger = LoggerFactory.getLogger(MCPWebSocketHandler.class);
    private final Map<String, WebSocketSession> sessions = new ConcurrentHashMap<>();
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    @Autowired
    private MCPService mcpService;
    
    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        logger.info("WebSocket connection established: {}", session.getId());
        sessions.put(session.getId(), session);
    }
    
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        String payload = message.getPayload();
        logger.debug("Received message: {}", payload);
        
        try {
            JsonNode jsonNode = objectMapper.readTree(payload);
            String type = jsonNode.path("type").asText();
            
            switch (type) {
                case "list_resources":
                    handleListResources(session, jsonNode);
                    break;
                case "read_resource":
                    handleReadResource(session, jsonNode);
                    break;
                default:
                    sendErrorResponse(session, "Unsupported message type: " + type);
            }
        } catch (Exception e) {
            logger.error("Error processing message", e);
            sendErrorResponse(session, "Error processing message: " + e.getMessage());
        }
    }
    
    private void handleListResources(WebSocketSession session, JsonNode request) throws IOException {
        String cursor = request.path("cursor").asText(null);
        MCPListResourcesResponse response = mcpService.listResources(cursor);
        sendResponse(session, response);
    }
    
    private void handleReadResource(WebSocketSession session, JsonNode request) throws IOException {
        String uri = request.path("uri").asText();
        if (uri == null || uri.isEmpty()) {
            sendErrorResponse(session, "URI is required for read_resource");
            return;
        }
        
        MCPResourceResponse response = mcpService.readResource(uri);
        sendResponse(session, response);
    }
    
    private void sendResponse(WebSocketSession session, Object response) throws IOException {
        String responseStr = objectMapper.writeValueAsString(response);
        session.sendMessage(new TextMessage(responseStr));
    }
    
    private void sendErrorResponse(WebSocketSession session, String errorMessage) throws IOException {
        ObjectNode errorResponse = objectMapper.createObjectNode()
                .put("status", "error")
                .put("message", errorMessage);
        sendResponse(session, errorResponse);
    }
    
    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        logger.info("WebSocket connection closed: {}, status: {}", session.getId(), status);
        sessions.remove(session.getId());
    }
}
