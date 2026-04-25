---
type: skill
name: Api Design
description: Project-specific guidance for introducing Python interfaces and boundaries in whispr-codex
skillSlug: api-design
phases: [P, E]
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Identifique o novo contrato em `src/whispr/` antes de pensar em CLI ou config.
2. Reaproveite `AppConfig`, `WhisperCppEngine` e `DictationController` quando o requisito for apenas uma nova fonte de entrada.
3. Prefira interfaces pequenas e sincrono/assinado explicito.
4. Exponha configuracao nova somente quando houver uso operacional real.

## Examples

```text
Bom candidato: criar um adaptador de updates do Telegram que entregue audio bruto para o pipeline atual.
Mau candidato: duplicar `DictationApp` inteiro so porque a origem do audio mudou.
```

## Quality Bar

- Cada nova abstracao deve apontar para um modulo existente que ela simplifica.
- Contratos precisam ser testaveis sem Windows real nem rede real.
- Nomes devem refletir papel operacional, nao tecnologia passageira.

## Resource Strategy

- Adicione `references/` apenas para protocolos externos como Telegram.
- Evite criar scripts auxiliares ate o fluxo ficar repetitivo.
