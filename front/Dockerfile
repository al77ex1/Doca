FROM node:20-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application
COPY . .

# Set environment variable for development or production
ARG NODE_ENV=development
ENV NODE_ENV=${NODE_ENV}

# Expose port
EXPOSE 5173

# Start command - development by default
CMD ["npm", "run", "dev:docker"]
