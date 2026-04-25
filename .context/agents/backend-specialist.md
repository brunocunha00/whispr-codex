---
type: agent
name: backend-specialist
description: Backend/runtime playbook for whispr-codex
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Backend Specialist

## Responsibilities

- Trabalhar nos modulos Python de runtime em `src/whispr/`.
- Modelar servicos auxiliares para download de audio, parsing de eventos e execucao de transcricao.
- Manter mensagens de erro operacionais legiveis no terminal.

## Key Files

- `src/whispr/app.py`
- `src/whispr/audio.py`
- `src/whispr/engine.py`
- `src/whispr/cli.py`

## Repository-specific Checks

- Reaproveitar `WhisperCppEngine` antes de introduzir outro backend.
- Nao depender de estado global escondido; preferir objetos explicitamente injetados.
- Manter a configuracao extensivel em `AppConfig`.

## Expected Handoffs

- Coordenar com `security-auditor` ao introduzir tokens ou APIs externas.
- Coordenar com `test-writer` para cobrir novos fluxos de erro e fallback.
