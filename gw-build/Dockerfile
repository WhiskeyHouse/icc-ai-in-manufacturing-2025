ARG IGNITION_VERSION=${IGNITION_VERSION}
ARG GIT_USER_TOKEN=${GIT_USER_TOKEN}
FROM inductiveautomation/ignition:${IGNITION_VERSION} as prep

# Temporarily become root for system-level updates (required for 8.1.26+)
USER root

# Change permissions on tmp folder after getting error with 8.1.33
RUN touch /tmp/test
RUN chmod 777 /tmp 

# After the apt-get update in the prep stage
RUN apt-get update && apt-get install -y wget ca-certificates jq zip unzip sqlite3 openssl

# Add certificate generation
RUN mkdir -p /usr/local/share/ca-certificates/ignition
RUN openssl req -x509 -newkey rsa:4096 -keyout /usr/local/share/ca-certificates/ignition/gateway.key \
  -out /usr/local/share/ca-certificates/ignition/gateway.crt -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=ignition-spoke1"

# Update CA certificates
RUN chmod 644 /usr/local/share/ca-certificates/ignition/gateway.crt \
  && update-ca-certificates


ARG SUPPLEMENTAL_AZUREIOTINJECTOR_DOWNLOAD_URL="https://files.inductiveautomation.com/third-party/cirrus-link/4.0.15/Azure-Injector-signed.modl"
ARG SUPPLEMENTAL_AZUREIOTINJECTOR_DOWNLOAD_SHA256="e952629cebaad75825cf6e57c09c01f5f1772065a6e87cc0cda45fdca4b29f13"
ARG SUPPLEMENTAL_MQTTTRANSMISSION_DOWNLOAD_URL="https://files.inductiveautomation.com/third-party/cirrus-link/4.0.15/MQTT-Transmission-signed.modl"
ARG SUPPLEMENTAL_MQTTTRANSMISSION_DOWNLOAD_SHA256="1e1e7428cba02dce6e579e6c82e4b8ad30d892438a7504aa0481eff7a5f87952"
ARG SUPPLEMENTAL_MQTTTRANSMISSIONNIGHTLY_DOWNLOAD_URL="https://ignition-modules-nightly.s3.amazonaws.com/Ignition8/MQTT-Transmission-signed.modl"
ARG SUPPLEMENTAL_MQTTTRANSMISSIONNIGHTLY_DOWNLOAD_SHA256="notused"
ARG SUPPLEMENTAL_MQTTENGINE_DOWNLOAD_URL="https://files.inductiveautomation.com/third-party/cirrus-link/4.0.15/MQTT-Engine-signed.modl"
ARG SUPPLEMENTAL_MQTTENGINE_DOWNLOAD_SHA256="5693c22b391e6da31351f2bb9245ad65e96dff9d02c0a322cb70eb11a2fb86b6"
ARG SUPPLEMENTAL_MQTTENGINENIGHTLY_DOWNLOAD_URL="https://ignition-modules-nightly.s3.amazonaws.com/Ignition8/MQTT-Engine-signed.modl"
ARG SUPPLEMENTAL_MQTTENGINENIGHTLY_DOWNLOAD_SHA256="notused"
ARG SUPPLEMENTAL_MQTTDISTRIBUTOR_DOWNLOAD_URL="https://files.inductiveautomation.com/third-party/cirrus-link/4.0.15/MQTT-Distributor-signed.modl"
ARG SUPPLEMENTAL_MQTTDISTRIBUTOR_DOWNLOAD_SHA256="5c81be13a9f749899825a99a109502c1eb28be940d060301a1ddf9967d488f9e"
ARG SUPPLEMENTAL_MQTTDISTRIBUTORNIGHTLY_DOWNLOAD_URL="https://ignition-modules-nightly.s3.amazonaws.com/Ignition8/MQTT-Distributor-signed.modl"
ARG SUPPLEMENTAL_MQTTDISTRIBUTORNIGHTLY_DOWNLOAD_SHA256="notused"
ARG SUPPLEMENTAL_GIT_DOWNLOAD_URL="https://whkdev01storage.blob.core.windows.net/plugpackages/Git-signed.modl"
ARG SUPPLEMENTAL_GIT_DOWNLOAD_SHA256="notused"
ARG SUPPLEMENTAL_MODULES


# Set working directory for this prep image and ensure that exits from sub-shells bubble up and report an error
WORKDIR /root
SHELL [ "/usr/bin/env", "-S", "bash", "-euo", "pipefail", "-O", "inherit_errexit", "-c" ]

# Retrieve all targeted modules and verify their integrity
COPY --chmod=0755 retrieve-modules.sh .
RUN bash retrieve-modules.sh \
  -m "${SUPPLEMENTAL_MODULES:-}"

# Supplement other default environment variables
ENV ACCEPT_IGNITION_EULA=Y \
  IGNITION_EDITION=standard \
  GATEWAY_MODULES_ENABLED=all \ 
  DISABLE_QUICKSTARTS=true \
  ACCEPT_MODULE_EULAS=Y \
  ACCEPT_THIRD_PARTY_EULAS=Y

# Install and register modules
COPY --chmod=0755 register-module.sh ./
RUN shopt -s nullglob; \
  for module in *.modl; do \
  echo "Found module: ${module}"; \
  done; \
  shopt -u nullglob

# Final Image
FROM inductiveautomation/ignition:${IGNITION_VERSION} as final

COPY --chown=ignition:ignition ssl.pfx /usr/local/bin/ignition/data/local/ssl.pfx

# Temporarily become root for system-level updates (required for 8.1.26+)
USER root

# Change permissions on tmp folder after getting error with 8.1.33
RUN chmod 777 /tmp 

# Add supplemental packages, such as git if needed/desired
RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  git && \
  rm -rf /var/lib/apt/lists/*


# Copy mysql jdbc jar into user-lib/jdbc dir
COPY --chown=ignition:ignition mysql-connector-j-8.3.0.jar ${IGNITION_INSTALL_LOCATION}/user-lib/jdbc/mysql-connector-j-8.3.0.jar
# Embed modules and base gwbk from prep image as well as entrypoint shim
COPY --from=prep --chown=ignition:ignition /root/*.modl ${IGNITION_INSTALL_LOCATION}/user-lib/modules/
# No base GWBK - will create fresh gateway configuration
COPY --chmod=0755 --chown=root:root docker-entrypoint-shim.sh /usr/local/bin/
COPY --chmod=0755 --chown=root:root register-password.sh /usr/local/bin/

# Git user token no longer needed without MES client

# Removed WhiskeyHouse MES GraphQL client - proprietary content

RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates

# Copy ignition configuration
COPY --chown=ignition:ignition ignition.conf ${IGNITION_INSTALL_LOCATION}/data/ignition.conf

# Return to ignition user
WORKDIR ${IGNITION_INSTALL_LOCATION}
USER ignition

# Git configuration removed - no longer needed without MES client

# In the final stage, after copying other files
COPY --from=prep --chown=ignition:ignition /usr/local/share/ca-certificates/ignition/ ${IGNITION_INSTALL_LOCATION}/certificates/


# Target the entrypoint shim for any custom logic prior to gateway launch
ENTRYPOINT [ "docker-entrypoint-shim.sh" ]