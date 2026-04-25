---
type: skill
name: Refactoring
description: Refactoring guidance for whispr-codex
skillSlug: refactoring
phases: [E]
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Prenda o comportamento atual com teste ou reproducao confiavel.
2. Extraia uma costura de cada vez, normalmente em `app.py` ou `engine.py`.
3. Rode `pytest` apos cada passo relevante.
4. Verifique se mensagens de erro e defaults de config continuam iguais.

## Examples

```text
Refactor util: extrair uma interface de fonte de audio sem mexer na logica de `StablePrefixCommitter`.
```

## Quality Bar

- Sem mudanca de comportamento acidental.
- Sem duplicar pipeline atual para nova origem de audio.
- Refatoracoes devem facilitar testes, nao dificultar.

## Resource Strategy

- Scripts extras raramente sao necessarios.
