---
type: skill
name: Code Review
description: Project-specific review guidance for whispr-codex
skillSlug: code-review
phases: [R, V]
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Leia o objetivo da mudanca e os arquivos centrais tocados.
2. Procure regressao em `app.py`, `engine.py`, `config.py` e `injector.py`.
3. Verifique se `tests/` cobrem o novo comportamento observavel.
4. Liste riscos antes de comentarios cosméticos.

## Examples

```text
Se uma feature adiciona Telegram, revise:
- autorizacao de chat
- download de audio
- reutilizacao correta de `WhisperCppEngine`
- impacto no fluxo atual `whispr run`
```

## Quality Bar

- Findings devem citar arquivo e efeito real.
- Foco em comportamento, seguranca e testes.
- Nao pedir abstrações extras sem ganho claro.

## Resource Strategy

- Nao crie artefatos extras se um comentario curto resolver.
