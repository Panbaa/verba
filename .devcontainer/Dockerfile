FROM mcr.microsoft.com/devcontainers/base:ubuntu

ENV PNPM_HOME="/usr/local/share/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends ca-certificates curl gnupg; \
	mkdir -p /etc/apt/keyrings; \
	curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg; \
	echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" > /etc/apt/sources.list.d/nodesource.list; \
	apt-get update; \
	apt-get install -y --no-install-recommends nodejs; \
	corepack enable; \
	corepack prepare pnpm@latest --activate; \
	mkdir -p "$PNPM_HOME"; \
	chmod 755 "$PNPM_HOME"; \
	pnpm config set global-bin-dir "$PNPM_HOME"; \
	pnpm add -g opencode-ai@latest @fission-ai/openspec@latest; \
	rm -rf /var/lib/apt/lists/*
