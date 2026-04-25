---
type: doc
name: development-workflow
description: Day-to-day engineering processes, branching, and contribution guidelines
category: workflow
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Development Workflow

O fluxo cotidiano neste repositorio e simples: ajustar codigo Python em `src/whispr`, validar com `pytest`, revisar os comandos do CLI manualmente e, quando necessario, gerar a distribuicao portatil. Como o projeto depende de recursos Windows e binarios locais, parte da verificacao continua sendo manual.

## Branching & Releases

- O repositorio nao expõe um modelo formal de branching; assuma ramificacoes curtas e focadas.
- Versoes ficam em `pyproject.toml` e no pacote Python.
- Releases de distribuicao passam por `scripts/build-portable.ps1`.
- `dist-portable/` deve ser tratado como saida gerada, nao como area de trabalho principal.

## Local Development

- Instalar dependencias:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

- Rodar testes:

```powershell
python -m pytest
```

- Inicializar config local:

```powershell
python -m whispr init-config
```

- Validar setup:

```powershell
python -m whispr doctor
python -m whispr devices
python -m whispr benchmark
```

- Executar o app:

```powershell
python -m whispr run
```

## Code Review Expectations

Mudancas devem preservar o fluxo de ditado incremental, nao quebrar o caminho Windows-first e manter o comportamento coberto pelos testes existentes. Revisoes merecem foco em regressao de transcricao parcial/final, uso de APIs do Windows, compatibilidade com `whisper.cpp` e mensagens de erro operacionais.

## Onboarding Tasks

Quem entrar no projeto deve primeiro configurar `whisper.cpp`, gerar `config.toml`, rodar `doctor` e entender `DictationController` em `src/whispr/app.py`. Depois disso, vale ler `tests/test_app.py` e `tests/test_engine.py` para enxergar os contratos mais sensiveis.

## Related Resources

- [testing-strategy.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/testing-strategy.md:1)
- [tooling.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/tooling.md:1)
