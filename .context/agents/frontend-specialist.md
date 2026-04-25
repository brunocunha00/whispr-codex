---
type: agent
name: frontend-specialist
description: UI playbook for whispr-codex
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Frontend Specialist

## Responsibilities

- Trabalhar apenas na interface local existente: terminal `rich` e overlay Tk.
- Melhorar feedback visual sem transformar o app em interface web.

## Key Files

- `src/whispr/overlay.py`
- `src/whispr/cli.py`
- `src/whispr/app.py`

## Repository-specific Checks

- O overlay precisa continuar opcional.
- Mudancas visuais nao podem bloquear captura ou encerramento.
- Evitar dependencia nova de framework grafico sem necessidade real.
