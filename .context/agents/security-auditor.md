---
type: agent
name: security-auditor
description: Security review playbook for whispr-codex
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Security Auditor

## Responsibilities

- Revisar introducao de segredos, tokens e trafego externo.
- Verificar manipulacao de clipboard, arquivos temporarios e logs.
- Cobrar restricoes de origem ao aceitar mensagens remotas.

## Repository-specific Checks

- Segredos nao devem aparecer em `README.md`, `pyproject.toml` ou `dist-portable/`.
- Audio temporario deve continuar sob controle de `temp_dir`.
- Integracoes com Telegram precisam limitar chat IDs e validar tipo de mensagem antes de processar.
