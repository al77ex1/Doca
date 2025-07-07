package org.doca.config;

import io.github.cdimascio.dotenv.Dotenv;
import io.github.cdimascio.dotenv.DotenvEntry;

import java.util.Set;

public class EnvConfig {
    private EnvConfig() {}

    public static void loadEnvVariables() {
        Dotenv dotenv = Dotenv.load();
        Set<DotenvEntry> entries = dotenv.entries();

        for (DotenvEntry entry : entries) {
            System.setProperty(entry.getKey(), entry.getValue());
        }
    }
}
