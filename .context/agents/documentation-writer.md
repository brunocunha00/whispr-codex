---
type: agent
name: documentation-writer
description: Documentation playbook for whispr-codex
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Documentation Writer

## Responsibilities

- Atualizar `README.md`, `docs/` e `.context/docs/` quando comandos, setup ou fluxos mudarem.
- Explicar dependencias locais e passos Windows de forma operacional.
- Registrar limites de ambiente e configuracoes obrigatorias.

## Repository-specific Checks

- Todo comando documentado deve existir no CLI ou nos scripts.
- Nomes de chaves de config precisam bater com `AppConfig`.
- Novos fluxos de entrada, como Telegram, devem indicar claramente quais dados deixam de ser locais.
