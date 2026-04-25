---
type: doc
name: architecture
description: System architecture, layers, patterns, and design decisions
category: architecture
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Architecture Notes

`whispr-codex` e um aplicativo CLI monolitico para Windows. Ele captura audio do microfone enquanto uma hotkey global esta pressionada, transcreve localmente via `whisper.cpp` e injeta ou exibe o texto resultante no terminal e na janela em foco.

## System Architecture Overview

O fluxo principal nasce no CLI `whispr`, carrega configuracao de disco, instancia um `DictationApp` e entra em um loop de polling curto. A captura de audio e a hotkey alimentam um controlador em memoria; o controlador envia janelas PCM para `whisper-cli`, estabiliza hipoteses parciais e encaminha apenas o delta de texto para o injetor.

## Architectural Layers

- **CLI e bootstrap**: `src/whispr/cli.py` monta comandos, valida pre-requisitos e cria `DictationApp`.
- **Orquestracao de runtime**: `src/whispr/app.py` conecta hotkey, microfone, transcricao, overlay e injecao.
- **Captura de audio**: `src/whispr/audio.py` integra com `sounddevice`, gerencia buffers PCM e grava WAV temporario.
- **Inferencia local**: `src/whispr/engine.py` chama `whisper-cli`, tenta `vulkan` antes de `cpu` e normaliza a saida.
- **Estabilizacao de texto**: `src/whispr/stabilization.py` calcula prefixo estavel para evitar reinjecoes erradas.
- **Integracao com Windows**: `src/whispr/hotkey.py`, `src/whispr/injector.py` e `src/whispr/overlay.py` dependem de APIs locais e comportamento Windows-first.
- **Configuracao e diagnostico**: `src/whispr/config.py` e `src/whispr/diagnostics.py` centralizam paths, validacoes e checks operacionais.

## Detected Design Patterns

| Pattern | Confidence | Locations | Description |
|---|---:|---|---|
| Controller | High | `src/whispr/app.py` | `DictationController` coordena captura, transcricao parcial/final e saida. |
| Strategy | High | `src/whispr/injector.py` | `create_injector()` escolhe `auto`, `clipboard` ou `sendinput`. |
| Adapter | Medium | `src/whispr/engine.py` | `WhisperCppEngine` adapta `whisper-cli` para uma API Python interna. |
| Null Object | High | `src/whispr/overlay.py` | `NullCaptureIndicator` remove efeitos visuais sem condicionais no fluxo principal. |

## Entry Points

- [src/whispr/cli.py](/D:/repositorio/bc-developer/whispr-codex/src/whispr/cli.py:1)
- [src/whispr/__main__.py](/D:/repositorio/bc-developer/whispr-codex/src/whispr/__main__.py:1)
- [src/whispr/app.py](/D:/repositorio/bc-developer/whispr-codex/src/whispr/app.py:1)

## Public API

| Symbol | Type | Location |
|---|---|---|
| `AppConfig` | dataclass | `src/whispr/config.py` |
| `DictationApp` | class | `src/whispr/app.py` |
| `DictationController` | class | `src/whispr/app.py` |
| `WhisperCppEngine` | class | `src/whispr/engine.py` |
| `create_injector` | function | `src/whispr/injector.py` |
| `create_capture_indicator` | function | `src/whispr/overlay.py` |

## Internal System Boundaries

O projeto nao possui camadas de persistencia, rede ou filas. As fronteiras relevantes sao: captura de audio em tempo real, subprocesso de inferencia local, e automacao de entrada de texto no Windows. Isso reduz complexidade operacional, mas aumenta o acoplamento com sistema operacional e com o executavel externo `whisper-cli`.

## External Service Dependencies

- `whisper.cpp` via `whisper-cli.exe`: dependencia obrigatoria para inferencia local.
- `sounddevice`: captura do microfone.
- `keyboard`: hotkey global no Windows.
- `tkinter`: overlay visual opcional.

## Key Decisions & Trade-offs

O projeto prefere inferencia local a servicos externos para reduzir latencia, custo recorrente e exposicao de dados. Em troca, o setup depende de um binario local, modelo `ggml` e uma stack Windows sensivel a drivers e permissao de input global.

## Risks & Constraints

O runtime assume `sample_rate = 16000`, Windows e foco em uma unica janela de destino. O diretório `dist-portable/` domina a contagem de arquivos do repositorio, mas representa artefato empacotado e nao codigo-fonte ativo.

## Top Directories Snapshot

- `src/` - codigo Python principal e entry points.
- `tests/` - testes de unidade para config, engine, injecao, estabilidade e app.
- `scripts/` - bootstrap de `whisper.cpp` e build portatil.
- `docs/` - setup manual para Windows.
- `dist-portable/` - artefatos gerados para distribuicao.

## Related Resources

- [project-overview.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/project-overview.md:1)
- [data-flow.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/data-flow.md:1)
- [tooling.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/tooling.md:1)
