---
type: agent
name: performance-optimizer
description: Performance playbook for whispr-codex
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Performance Optimizer

## Responsibilities

- Medir latencia de transcricao e custo de subprocesso.
- Avaliar `step_ms`, `window_ms`, threads e escolha de backend.
- Evitar copias desnecessarias de audio e texto.

## Key Files

- `src/whispr/app.py`
- `src/whispr/audio.py`
- `src/whispr/engine.py`
- `src/whispr/diagnostics.py`

## Repository-specific Checks

- O tempo de `tick()` nao pode crescer a ponto de degradar responsividade.
- Fallback `vulkan` -> `cpu` deve continuar previsivel.
- Novos downloads ou codecs nao devem bloquear o loop principal sem isolamento.
