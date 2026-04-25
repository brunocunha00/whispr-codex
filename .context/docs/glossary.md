---
type: doc
name: glossary
description: Project terminology, type definitions, domain entities, and business rules
category: glossary
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Glossary & Domain Concepts

Este projeto gira em torno de ditado local com captura push-to-talk, transcricao incremental e injecao de texto. Os termos abaixo aparecem repetidamente no codigo e sao importantes para qualquer extensao, inclusive uma futura integracao com Telegram.

## Type Definitions

- [src/whispr/config.py](/D:/repositorio/bc-developer/whispr-codex/src/whispr/config.py:45) - `AppConfig`
- [src/whispr/engine.py](/D:/repositorio/bc-developer/whispr-codex/src/whispr/engine.py:18) - `TranscriptionResult`
- [src/whispr/diagnostics.py](/D:/repositorio/bc-developer/whispr-codex/src/whispr/diagnostics.py:13) - `DoctorCheck`
- [src/whispr/diagnostics.py](/D:/repositorio/bc-developer/whispr-codex/src/whispr/diagnostics.py:68) - `BenchmarkResult`
- [src/whispr/app.py](/D:/repositorio/bc-developer/whispr-codex/src/whispr/app.py:17) - `DictationSession`

## Enumerations

- Nao ha `Enum` Python formal no codigo atual.
- O projeto usa conjuntos de valores validos em `config.py` para representar enums de fato: `VALID_BACKENDS`, `VALID_COMMIT_MODES`, `VALID_INJECT_MODES`, `VALID_INJECT_TARGETS` e `VALID_INDICATOR_POSITIONS`.

## Core Terms

- **Push-to-talk**: modo em que a captura so ocorre enquanto a tecla configurada esta pressionada.
- **SessionAudioBuffer**: buffer em memoria dos bytes PCM de uma sessao de ditado.
- **Stable prefix**: porcao do texto parcial considerada suficientemente estavel para ser enviada sem precisar apagar depois.
- **Flush final**: transcricao completa emitida ao soltar a hotkey.
- **Backend auto**: estrategia que tenta `vulkan` e cai para `cpu`.
- **Injector**: camada responsavel por colar/digitar o texto na janela ativa.
- **Portable mode**: execucao congelada em que config e modelos ficam ao lado do executavel.

## Acronyms & Abbreviations

- **PCM**: Pulse-code modulation, formato bruto de audio usado no buffer.
- **VAD**: Voice Activity Detection; opcionalmente suportado via `vad_model_path`.
- **CLI**: Command-line interface.
- **REC**: indicador visual exibido no overlay durante captura.

## Personas / Actors

O ator principal e o usuario local em Windows que quer ditar texto sem depender de cloud. Um ator secundario e o mantenedor tecnico, que precisa diagnosticar setup de microfone, modelo e binario `whisper.cpp`.

## Domain Rules & Invariants

- `sample_rate` deve permanecer em `16000` na v1.
- `window_ms` deve ser maior ou igual a `step_ms`.
- Apenas texto novo e estavel deve ser injetado incrementalmente.
- O sistema foi desenhado para Windows; outras plataformas falham cedo.

## Related Resources

- [project-overview.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/project-overview.md:1)
- [architecture.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/architecture.md:1)
