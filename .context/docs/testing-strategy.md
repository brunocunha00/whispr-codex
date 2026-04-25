---
type: doc
name: testing-strategy
description: Automated and manual testing approach for the repository
category: testing
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Testing Strategy

O repositorio combina testes unitarios rapidos para regras de negocio e verificacao manual para integracoes Windows, captura de audio e `whisper.cpp`. O objetivo dos testes automatizados e proteger contratos pequenos e deterministas; hardware, subprocessos reais e automacao de desktop continuam fora da suite padrao.

## Automated Coverage

- `tests/test_app.py` cobre `DictationController` com doubles de engine, injector e indicador.
- `tests/test_engine.py` valida limpeza de transcriptos e montagem de comandos do engine.
- `tests/test_config.py` protege validacoes de configuracao e resolucao de caminhos.
- `tests/test_injector.py` e `tests/test_stabilization.py` cobrem partes puras ou semi-puras do fluxo de texto.

## Test Levels

- **Unitario**: logica de string, validacoes de config e montagem de comandos.
- **Com integracao fakeada**: controlador principal usando dependencias simuladas.
- **Manual**: microfone real, hotkey global, overlay e `whisper-cli` no Windows.

## Local Commands

```powershell
python -m pytest
python -m whispr doctor
python -m whispr benchmark
```

## What Needs Manual Verification

- Detecao do microfone pela stack local.
- Funcionamento de `keyboard` com hotkey global.
- Clipboard restore e fallback de `SendInput`.
- Build portatil gerado por `scripts/build-portable.ps1`.
- Qualidade/latencia de transcricao com modelos reais.

## Coverage Gaps

Nao ha testes automatizados de overlay Tk, stream de audio real, subprocesso real do `whisper-cli` nem build com `pyinstaller`. Uma extensao com Telegram deve adicionar testes unitarios para parsing de updates, autorizacao de chat e pipeline de download/transcricao.

## Quality Gates

- `pytest` deve permanecer verde.
- Comandos `doctor` e `run` precisam falhar de forma explicita quando faltarem binario ou modelo.
- Mudancas em `app.py`, `engine.py` e `injector.py` exigem revisao manual do fluxo de ponta a ponta.

## Related Resources

- [development-workflow.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/development-workflow.md:1)
- [data-flow.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/data-flow.md:1)
