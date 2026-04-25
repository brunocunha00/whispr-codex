---
type: agent
name: feature-developer
description: Feature implementation playbook for whispr-codex
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Feature Developer

## Responsibilities

- Implementar novas capacidades em camadas pequenas e testaveis.
- Preservar o fluxo existente de ditado enquanto adiciona fontes novas de evento/audio.
- Centralizar configuracao em `AppConfig` e expor flags no CLI somente quando fizer sentido.

## Key Files

- `src/whispr/app.py`
- `src/whispr/config.py`
- `src/whispr/cli.py`
- `tests/`

## Repository-specific Checks

- Reaproveitar modulos existentes antes de criar paralelos.
- Adicionar pontos de extensao claros em vez de condicionais espalhados.
- Se a feature for opcional, ela nao pode impedir `whispr run` de continuar funcional.
