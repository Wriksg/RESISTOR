# ==========================================
# STAGE 1: Build the React/Vite Frontend
# ==========================================
FROM node:20-alpine AS build

# Set working directory
WORKDIR /app

# Copy the frontend package.json files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code (including the src/data JSON files!)
COPY frontend/ .

# Build the production static files
RUN npm run build

# ==========================================
# STAGE 2: Serve with Nginx
# ==========================================
FROM nginx:alpine

# Copy the built React app from Stage 1 into Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 for web traffic
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]