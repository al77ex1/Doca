# Stage 1: Build
FROM maven:3-eclipse-temurin-17-alpine AS build
WORKDIR /workspace/app

# Copy Maven settings and POM first
COPY pom.xml ./

# Download all dependencies and plugins
RUN --mount=type=cache,target=/root/.m2 mvn -B dependency:resolve-plugins dependency:resolve

# Copy source files and build
COPY ./src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -B -f ./pom.xml package -DskipTests

# Create a custom JRE
RUN apk add --no-cache binutils && \
    cd /opt/java/openjdk && \
    jlink \
    --add-modules java.base,java.xml,java.naming,java.desktop,java.rmi,jdk.crypto.ec,java.management,java.management.rmi,java.instrument,java.security.jgss,java.security.sasl,java.sql,java.transaction.xa,java.logging,jdk.unsupported \
    --strip-debug \
    --no-man-pages \
    --no-header-files \
    --compress=2 \
    --output /jre/minimal-jre

# Stage 2: Runtime
FROM alpine:3.19
WORKDIR /app

# Create a non-root user first
RUN addgroup -S spring && adduser -S spring -G spring && \
    mkdir -p /app/logs && chown -R spring:spring /app

# Copy JRE and application files in a single layer
COPY --from=build --chown=spring:spring /jre/minimal-jre /opt/java/openjdk
COPY --from=build --chown=spring:spring /workspace/app/target/OnyxEducation-1.0-SNAPSHOT.jar /app/app.jar

# Copy .env file
COPY --chown=spring:spring .env /app/.env

# Set environment variables
ENV PATH="/opt/java/openjdk/bin:${PATH}" \
    JAVA_TOOL_OPTIONS="-Xmx512m"

# Use non-root user
USER spring:spring

EXPOSE 8080/tcp

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
