# Build eda-frontend
FROM docker.io/node:16-alpine AS ui-builder
WORKDIR /app

COPY . $WORKDIR

RUN cd ui && npm install && npm run build

FROM docker.io/nginx
ARG NGINX_CONF=tools/docker/nginx/default.conf
ARG NGINX_CONFIGURATION_PATH=/etc/nginx/conf.d/

ENV DIST_UI="/opt/app-root/ui/eda"

ADD ${NGINX_CONF} ${NGINX_CONFIGURATION_PATH}

# Copy dist dir to final location
RUN mkdir -p ${DIST_UI}/
COPY --from=ui-builder /app/ui/dist/ ${DIST_UI}

