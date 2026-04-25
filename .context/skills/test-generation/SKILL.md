---
type: skill
name: Test Generation
description: Test generation guidance for whispr-codex
skillSlug: test-generation
phases: [E, V]
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Localize o contrato observavel no modulo alterado.
2. Prefira teste unitario puro ou com doubles.
3. Cubra caminho feliz, erro e fallback.
4. So deixe validacao manual para aquilo que depende mesmo do Windows ou do binario real.

## Examples

```text
Para Telegram:
- parser de update
- filtro de chat permitido
- selecao do arquivo de audio correto
- chamada ao engine com bytes convertidos
```

## Quality Bar

- Testes devem rodar com `python -m pytest`.
- Nada de dependencias reais de rede.
- Fixtures curtas e nomes descritivos.

## Resource Strategy

- Criar fixtures pequenas em `tests/` quando isso simplificar o raciocinio.
