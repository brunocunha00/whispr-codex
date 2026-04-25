---
type: agent
name: database-specialist
description: Database playbook for whispr-codex
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Database Specialist

## Responsibilities

- Confirmar quando um requisito realmente precisa de persistencia.
- Evitar introduzir banco para problemas que podem ficar em memoria ou config local.

## Repository-specific Notes

- O projeto atual nao usa banco de dados.
- Estado de runtime fica em memoria (`DictationSession`, `SessionAudioBuffer`).
- Configuracao e baseada em arquivo TOML local.

## If Persistence Becomes Necessary

- Preferir armazenamento minimo e explicito.
- Definir politica clara para retencao de audio e transcricoes.
- Coordenar com `security-auditor` antes de persistir conteudo sensivel.
