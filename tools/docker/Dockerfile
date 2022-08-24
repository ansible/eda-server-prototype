# Build UI
FROM docker.io/node:16-alpine AS ui-builder
WORKDIR /app
COPY . $WORKDIR
RUN cd ui && npm install && npm run build


# Build app
FROM registry.access.redhat.com/ubi8/python-39
ARG USER_ID=${USER_ID:-1001}
ARG DEVEL_AE_LIBRARY=1
WORKDIR $HOME

USER 0
RUN pip install ansible && \
    ansible-galaxy collection install git+https://github.com/benthomasson/benthomasson-eda.git#benthomasson/eda/
COPY . $WORKDIR
COPY --from=ui-builder /app/ui/dist/ ./ui/dist
RUN chown -R $USER_ID ./

USER $USER_ID
RUN pip install .

RUN bash -c "if [ $DEVEL_AE_LIBRARY -ne 0 ]; then \
    pip uninstall ansible-events -y && \
    pip install git+https://github.com/benthomasson/ansible-events.git; fi"

CMD ["ansible-events-ui"]
