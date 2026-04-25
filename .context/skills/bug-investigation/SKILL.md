---
type: skill
name: Bug Investigation
description: Project-specific bug investigation workflow for whispr-codex
skillSlug: bug-investigation
phases: [R, E]
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Classifique a falha como config, captura, engine, estabilizacao, injecao ou build.
2. Reproduza com `pytest`, `whispr doctor` ou um fluxo manual minimo.
3. Isole o modulo com o menor teste ou fixture possivel.
4. Corrija e deixe evidencias objetivas do comportamento esperado.

## Examples

```text
Sintoma: texto final chega duplicado.
Alvo inicial: `StablePrefixCommitter.flush()` e `DictationController.on_release()`.
```

## Quality Bar

- Nao culpe `dist-portable/` antes de revisar `src/`.
- Sempre confirme se o bug e Windows-only ou logico.
- Preferir testes de regressao pequenos quando possivel.

## Resource Strategy

- Use fixtures curtas em `tests/` em vez de audio real longo.
