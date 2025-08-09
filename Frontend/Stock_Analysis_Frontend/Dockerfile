FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install Angular CLI globally
RUN npm install -g @angular/cli

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy all source code
COPY . .

# Expose Angular dev server port
EXPOSE 4200

# Enable live reload & run dev server
CMD ["ng", "serve", "--host", "0.0.0.0", "--port", "4200"]


# # Stage 1: Build
# FROM node:20-alpine as build

# WORKDIR /app
# COPY package*.json ./
# RUN npm ci
# COPY . .
# RUN npm run build --prod

# # Stage 2: Serve with nginx
# FROM nginx:alpine
# COPY --from=build /app/dist/your-app-name /usr/share/nginx/html
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]
