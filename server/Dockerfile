# Baut auf dem offiziellen xiaozhi-esp32-server-Basisimage auf (Python-Abhängigkeiten
# sind dort schon installiert) und zieht den Server-Code + unseren Anthropic-Adapter
# obendrauf. So bleibt dieses Repo klein und referenziert das Upstream-Projekt statt
# es zu vendoren.
FROM ghcr.io/xinnan-tech/xiaozhi-esp32-server:server-base

ARG XIAOZHI_SERVER_REF=main

RUN apt-get update && \
    apt-get install -y --no-install-recommends git gettext-base && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/xiaozhi-esp32-server

RUN git clone --depth 1 --branch ${XIAOZHI_SERVER_REF} \
        https://github.com/xinnan-tech/xiaozhi-esp32-server /tmp/xiaozhi-esp32-server && \
    cp -r /tmp/xiaozhi-esp32-server/main/xiaozhi-server/. . && \
    rm -rf /tmp/xiaozhi-esp32-server

# Anthropic-Claude-LLM-Provider als zusätzliches Plugin einhängen
COPY overlay/AnthropicLLM ./core/providers/llm/AnthropicLLM
RUN pip install --no-cache-dir anthropic

# Config-Template + Entrypoint, der data/.config.yaml aus Umgebungsvariablen erzeugt
COPY overlay/config.template.yaml ./data/.config.yaml.template
COPY overlay/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
