---
type: agent
name: test-writer
description: Test authoring playbook for whispr-codex
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Test Writer

## Responsibilities

- Escrever testes de unidade e integracao fakeada em `tests/`.
- Cobrir contratos de config, parsing, fallback e regras de estabilizacao.
- Isolar dependencias Windows ou de rede por doubles.

## Repository-specific Checks

- Preferir testes deterministas, sem microfone real e sem `whisper-cli` real.
- Cobrir novas funcoes de download/parsing de Telegram com fixtures pequenas.
- Validar regressao do fluxo parcial/final quando `app.py` mudar.
