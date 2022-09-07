# Build UI
FROM docker.io/node:16-alpine AS ui-builder
WORKDIR /app

COPY . $WORKDIR

RUN cd ui && npm install && npm run build

FROM nginx
ARG NGINX_CONF=tools/docker/nginx/default.conf
ARG NGINX_CONFIGURATION_PATH=/etc/nginx/conf.d/

ENV CERT_PATH="/opt/app-root/etc/nginx.d/certs"
ENV DIST_UI="/opt/app-root/ui/eda"

RUN mkdir -p ${CERT_PATH}

ADD ${NGINX_CONF} ${NGINX_CONFIGURATION_PATH}

# certs
ADD --chown=1001:1001 tools/certs/*.crt ${CERT_PATH}
ADD --chown=1001:1001 tools/certs/*.key ${CERT_PATH}

# Copy dist dir to final location
RUN mkdir -p ${DIST_UI}/
COPY --from=ui-builder /app/ui/dist/ ${DIST_UI}

