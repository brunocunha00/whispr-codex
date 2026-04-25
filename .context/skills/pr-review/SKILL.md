---
type: skill
name: Pr Review
description: Pull request review guidance for whispr-codex
skillSlug: pr-review
phases: [R, V]
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Confirme o objetivo do PR e os arquivos de maior risco.
2. Revise regressao funcional antes de estilo.
3. Cheque evidencias de teste e validacao manual.
4. Registre findings com severidade e impacto operacional.

## Examples

```text
PR de Telegram:
- risco alto se aceitar updates de qualquer chat
- risco medio se bloquear `whispr run` por timeout de rede
```

## Quality Bar

- Findings primeiro, resumo depois.
- Referenciar arquivos e comportamento observado.
- Apontar ausencia de testes quando relevante.

## Resource Strategy

- Nao gerar checklist separado sem necessidade.
