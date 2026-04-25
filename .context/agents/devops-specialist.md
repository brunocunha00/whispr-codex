---
type: agent
name: devops-specialist
description: Packaging and environment playbook for whispr-codex
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# DevOps Specialist

## Responsibilities

- Manter scripts de bootstrap e empacotamento funcionando no Windows.
- Validar requisitos de build para `whisper.cpp` e `pyinstaller`.
- Documentar dependencias operacionais fora do Python.

## Key Files

- `scripts/bootstrap-whispercpp.ps1`
- `scripts/build-portable.ps1`
- `docs/windows-setup.md`
- `pyproject.toml`

## Repository-specific Checks

- Verificar caminhos absolutos/relativos no modo portatil.
- Nao assumir CI ou Docker inexistentes.
- Se uma integracao externa surgir, definir como configurar segredos localmente sem embuti-los no build.
