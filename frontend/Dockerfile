FROM node:20-slim AS builder

WORKDIR /app

# Copy package files first (for layer caching)
# If package.json hasn't changed, Docker skips npm install on rebuild
COPY package.json package-lock.json ./

# Install all npm dependencies
# --legacy-peer-deps = handle peer dependency conflicts (needed for our project)
RUN npm install --legacy-peer-deps

# Copy all frontend source code
COPY . .

# Build the React app for production
# This runs: tsc + vite build → creates /app/dist folder
# The dist folder contains: index.html, assets/*.js, assets/*.css
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# ── Stage 2: Serve ───────────────────────────────────────────
# Start fresh with just Nginx (tiny Alpine Linux = ~5MB)
FROM nginx:alpine

# Remove default Nginx welcome page
RUN rm -rf /usr/share/nginx/html/*

# Copy ONLY the built files from Stage 1 (builder)
# Nothing else from Stage 1 comes along — no Node, no source code
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy our custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Port 80 = standard HTTP port that Nginx listens on
EXPOSE 80

# Nginx runs in foreground (daemon off) so Docker can manage it
CMD ["nginx", "-g", "daemon off;"]
