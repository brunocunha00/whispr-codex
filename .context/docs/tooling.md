---
type: doc
name: tooling
description: Tooling, scripts, dependencies, and local development environment
category: tooling
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Tooling

O desenvolvimento gira em torno de Python local no Windows, um checkout do `whisper.cpp` compilado externamente e scripts PowerShell para bootstrap e empacotamento. Nao ha CI ou Docker declarados; o ambiente do desenvolvedor e parte importante do resultado.

## Runtime Dependencies

- `typer` - CLI.
- `rich` - tabelas e logs no terminal.
- `sounddevice` - captura de audio.
- `keyboard` - hotkey global.
- `numpy` - dependencia auxiliar do ecossistema de audio/build.

## Build & Packaging

- `pyinstaller` em extra `build`.
- `scripts/build-portable.ps1` monta a pasta `dist-portable/whispr`.
- `scripts/bootstrap-whispercpp.ps1` clona/compila `whisper.cpp` com opcao de Vulkan.

## Local Environment

- Python 3.13+
- Windows 10/11
- CMake 3.27+
- Visual Studio Build Tools ou MSVC equivalente
- Driver com suporte a Vulkan para caminho GPU opcional

## Frequently Used Commands

```powershell
python -m pip install -e .[dev]
python -m pytest
python -m whispr doctor
python -m whispr run
```

## Operational Files

- `pyproject.toml` - dependencias, entry point e configuracao do pytest.
- `README.md` - setup, comandos e distribuicao portatil.
- `docs/windows-setup.md` - orientacoes adicionais de setup.
- `%APPDATA%\whispr\config.toml` - configuracao local em modo nao portatil.

## Constraints

Sem CI, cada mudanca depende mais de disciplina local. Como `dist-portable/` traz muitos binarios, buscas e analises devem priorizar `src/`, `tests/`, `scripts/` e `docs/`.

## Related Resources

- [project-overview.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/project-overview.md:1)
- [development-workflow.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/development-workflow.md:1)
