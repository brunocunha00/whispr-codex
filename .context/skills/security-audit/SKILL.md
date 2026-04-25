---
type: skill
name: Security Audit
description: Security audit guidance for whispr-codex
skillSlug: security-audit
phases: [R, V]
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Procure novas fronteiras de confianca: rede, segredos, arquivos temporarios e input global.
2. Verifique o caminho dos dados sensiveis da entrada ate logs e disco.
3. Confirme defaults seguros em config.
4. Relate findings por impacto real.

## Examples

```text
Checklist para Telegram:
- token fora do codigo
- allowlist de chat IDs
- rejeicao de mensagens nao-audio
- limpeza de downloads temporarios
```

## Quality Bar

- Foco em segredo, autorizacao e exposicao de dados.
- Nao confundir bug funcional com risco de seguranca.
- Exigir mitigacao concreta quando houver integracao externa.

## Resource Strategy

- Referencias externas so quando o protocolo exigir detalhes de auth.
