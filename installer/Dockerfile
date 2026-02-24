# Miner Scanner Installer Web Page
# Serves the install landing page and install.sh for curl | bash
#
# Build with optional ARG to set GitHub repo:
#   docker build --build-arg GITHUB_REPO=https://github.com/owner/miner-scanner -f installer/Dockerfile .

FROM nginx:alpine

# Set at build time to customize repo (GitHub Actions passes these)
ARG GITHUB_RAW_URL=https://raw.githubusercontent.com/miladkhalafi/pi-miner-scanner/main
ARG GITHUB_REPO=https://github.com/miladkhalafi/pi-miner-scanner

# Copy nginx config and web assets (context is repo root)
COPY installer/nginx.conf /etc/nginx/nginx.conf
COPY installer/index.html /usr/share/nginx/html/
COPY installer/install.sh /usr/share/nginx/html/

# Replace placeholders with build args
RUN sed -i "s|https://raw.githubusercontent.com/miladkhalafi/pi-miner-scanner/main|$GITHUB_RAW_URL|g" /usr/share/nginx/html/index.html && \
    sed -i "s|@@GITHUB_REPO@@|$GITHUB_REPO|g" /usr/share/nginx/html/install.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
