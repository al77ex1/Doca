package org.doca.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;
import org.springframework.web.socket.server.standard.ServletServerContainerFactoryBean;

@Configuration
@EnableWebSocket
public class MCPServerConfig implements WebSocketConfigurer {

    @Value("${spring.websocket.max-text-message-size:8192}")
    private int maxTextMessageSize;
    
    @Value("${spring.websocket.max-binary-message-size:8192}")
    private int maxBinaryMessageSize;
    
    @Value("${spring.websocket.max-session-idle-timeout:60000}")
    private long maxSessionIdleTimeout;

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(mcpWebSocketHandler(), "/mcp/ws")
               .setAllowedOrigins("*");
    }
    
    @Bean
    public MCPWebSocketHandler mcpWebSocketHandler() {
        return new MCPWebSocketHandler();
    }
    
    @Bean
    public ServletServerContainerFactoryBean createWebSocketContainer() {
        ServletServerContainerFactoryBean container = new ServletServerContainerFactoryBean();
        container.setMaxTextMessageBufferSize(maxTextMessageSize);
        container.setMaxBinaryMessageBufferSize(maxBinaryMessageSize);
        container.setMaxSessionIdleTimeout(maxSessionIdleTimeout);
        return container;
    }
}
