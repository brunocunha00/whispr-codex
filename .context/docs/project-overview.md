---
type: doc
name: project-overview
description: High-level overview of the project, its purpose, and key components
category: overview
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Project Overview

`whispr-codex` e uma CLI Windows-first de ditado local baseada em modelos Whisper executados via `whisper.cpp`. O projeto serve para capturar audio do microfone por hotkey global, produzir transcricao incremental e entregar texto para a janela ativa e para o terminal sem depender de um servico remoto.

## Codebase Reference

> **Semantic Snapshot**: use `context({ action: "getMap", section: "all" })` quando precisar de um resumo gerado de stack, estrutura e simbolos exportados. O snapshot atual ajuda, mas ainda exige leitura manual dos modulos principais porque o projeto inclui muitos artefatos empacotados em `dist-portable/`.

## Quick Facts

- Root: `D:\repositorio\bc-developer\whispr-codex`
- Linguagem principal: Python
- Plataformas alvo: Windows 10/11
- Entry point de CLI: `src/whispr/cli.py`
- Runtime principal: `src/whispr/app.py`

## Entry Points

- [src/whispr/cli.py](/D:/repositorio/bc-developer/whispr-codex/src/whispr/cli.py:1)
- [src/whispr/__main__.py](/D:/repositorio/bc-developer/whispr-codex/src/whispr/__main__.py:1)
- [README.md](/D:/repositorio/bc-developer/whispr-codex/README.md:1)

## Key Exports

- `AppConfig` concentra configuracao e resolucao de caminhos.
- `DictationApp` e `DictationController` montam o loop de execucao.
- `WhisperCppEngine` encapsula o binario externo de transcricao.
- `StablePrefixCommitter` evita reinjecoes instaveis.
- `create_injector()` e `create_capture_indicator()` abstraem as integracoes Windows.

## File Structure & Code Organization

- `src/whispr/` - codigo principal do aplicativo.
- `tests/` - testes unitarios e doubles de dependencias.
- `scripts/` - automacao para bootstrap de `whisper.cpp` e empacotamento.
- `docs/` - setup de ambiente Windows.
- `dist-portable/` - build portatil e dependencias embarcadas.

## Technology Stack Summary

O projeto usa Python 3.13+, `typer` para CLI, `rich` para saida no terminal, `sounddevice` para captura de audio e `keyboard` para hotkeys globais. O reconhecimento de fala roda fora do processo Python, via `whisper-cli.exe`, e a distribuicao portatil depende de `pyinstaller`.

## Development Tools Overview

Os comandos principais ficam expostos pela propria CLI `whispr`, enquanto `pytest` cobre a validacao automatizada basica. `scripts/bootstrap-whispercpp.ps1` e `scripts/build-portable.ps1` sao os utilitarios essenciais fora do runtime.

## Getting Started Checklist

1. Criar e ativar uma virtualenv Python 3.13+.
2. Instalar dependencias com `python -m pip install -e .[dev]`.
3. Rodar `python -m whispr init-config`.
4. Configurar `model_path` e `whisper_cpp_path` no `config.toml`.
5. Validar setup com `python -m whispr doctor`.
6. Rodar `python -m pytest`.
7. Testar o fluxo manual com `python -m whispr run`.

## Next Steps

As extensoes mais naturais partem do fluxo de entrada de audio. Uma integracao com Telegram, por exemplo, deve reaproveitar `WhisperCppEngine` e adicionar uma nova fonte de audio/eventos sem quebrar o caminho atual de push-to-talk local.

## Related Resources

- [architecture.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/architecture.md:1)
- [development-workflow.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/development-workflow.md:1)
- [tooling.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/tooling.md:1)
