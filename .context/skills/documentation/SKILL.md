---
type: skill
name: Documentation
description: Documentation guidance tailored to whispr-codex
skillSlug: documentation
phases: [P, C]
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Descubra se a mudanca afeta setup, config, comandos ou arquitetura.
2. Atualize `README.md`, `docs/windows-setup.md` ou `.context/docs/` conforme o publico.
3. Confirme que todos os nomes de comando e chave batem com o codigo.
4. Registre limites Windows-first e dependencias externas de forma explicita.

## Examples

```text
Nova integracao com Telegram:
- documentar token e chat permitido
- explicar download/transcricao de audio
- deixar claro o que continua local e o que passa pela API do Telegram
```

## Quality Bar

- Comandos devem ser executaveis no PowerShell.
- Config keys devem bater com `AppConfig`.
- Nada de placeholders apos merge.

## Resource Strategy

- Adicione referencias externas somente quando o protocolo exigir detalhe.
