# Build eda-server
FROM registry.access.redhat.com/ubi8/python-39
ARG USER_ID=${USER_ID:-1001}
WORKDIR $HOME

USER 0
RUN dnf install -y java-17-openjdk-devel maven
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk
ENV PIP_NO_BINARY=jpy

RUN pip install ansible && \
    ansible-galaxy collection install git+https://github.com/ansible/event-driven-ansible.git

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . $WORKDIR
RUN chown -R $USER_ID ./

USER $USER_ID
RUN pip install --no-deps -e .

CMD ["eda-server"]
