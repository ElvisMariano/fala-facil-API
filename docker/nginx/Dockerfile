FROM nginx:1.25-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf

# Create directory for Let's Encrypt certificates
RUN mkdir -p /etc/letsencrypt

# Create directory for logs
RUN mkdir -p /var/log/nginx \
    && touch /var/log/nginx/access.log \
    && touch /var/log/nginx/error.log \
    && chown -R nginx:nginx /var/log/nginx

# Create directory for static and media files
RUN mkdir -p /app/staticfiles /app/mediafiles \
    && chown -R nginx:nginx /app

# Use non-root user
USER nginx

# Expose ports
EXPOSE 80 443 