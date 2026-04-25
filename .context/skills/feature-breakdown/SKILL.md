---
type: skill
name: Feature Breakdown
description: Feature planning guidance for whispr-codex
skillSlug: feature-breakdown
phases: [P]
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Defina o fluxo de entrada, processamento e saida.
2. Separe infraestrutura externa de reutilizacao interna do pipeline existente.
3. Ordene tarefas por dependencia tecnica, nao por area do arquivo.
4. Feche com riscos, testes e criterios de aceite.

## Examples

```text
Feature: receber audio do Telegram e imprimir transcricao no terminal
1. Config de token/chat autorizado
2. Listener de updates
3. Download do audio
4. Adaptador para `WhisperCppEngine`
5. Saida no terminal
6. Testes de parsing e autorizacao
```

## Quality Bar

- Cada tarefa precisa apontar para um modulo alvo.
- Separar risco de rede/segredo do risco de transcricao.
- Deixar claro o que e opcional por config.

## Resource Strategy

- Use plano markdown, nao uma arvore de arquivos nova.
