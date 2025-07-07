package org.doca;

import org.doca.config.EnvConfig;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DocaApplication {
    public static void main(String[] args) {
        // Load environment variables from .env file
        EnvConfig.loadEnvVariables();
        
        SpringApplication.run(DocaApplication.class, args);
    }
}
