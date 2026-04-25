---
type: skill
name: Commit Message
description: Commit message guidance for whispr-codex
skillSlug: commit-message
phases: [C]
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Descreva a mudanca pelo efeito no produto ou no runtime.
2. Mantenha o assunto curto e no imperativo.
3. Use o corpo para explicar o por que quando houver trade-off tecnico.

## Examples

```text
Add Telegram audio intake pipeline
Refactor controller to support pluggable input sources
```

## Quality Bar

- Um commit por mudanca logica.
- Cite Telegram, whisper.cpp, config ou testes quando isso for o valor principal.
- Evite assuntos genericos como "update code".

## Resource Strategy

- Nenhum recurso extra costuma ser necessario.
