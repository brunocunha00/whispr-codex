---
type: doc
name: security
description: Security policies, authentication, secrets management, and compliance requirements
category: security
generated: 2026-04-23
status: filled
scaffoldVersion: "2.0.0"
---

# Security & Compliance Notes

O projeto nao implementa autenticacao de usuarios nem expõe API HTTP, mas lida com audio potencialmente sensivel, texto transcrito e automacao de input no desktop. O maior risco e operacional: caminhos de binarios/modelos inseguros, vazamento de texto via clipboard e integracoes futuras com tokens de terceiros.

## Authentication & Authorization

Hoje nao existe camada de auth local. O app assume um unico operador da maquina e opera com permissao do usuario logado. Se a integracao com Telegram for adicionada, ela introduzira uma fronteira real de autenticacao: token de bot, restricao de chat autorizado e validacao de origem das mensagens.

## Secrets & Sensitive Data

As configuracoes vivem em `%APPDATA%\whispr\config.toml` ou ao lado do executavel em modo portatil. O arquivo atual nao guarda segredos, mas uma futura chave de Telegram nao deve ser hardcoded em `src/` nem entrar em `dist-portable/` sem revisao; o caminho correto e variavel de ambiente ou config local fora de versionamento sensivel.

## Compliance & Policies

- Manter processamento de audio local sempre que possivel.
- Evitar logar conteudo completo de audio/transcricao em ambiente compartilhado.
- Limitar artefatos WAV temporarios com `keep_wav_artifacts = false` por padrao.
- Documentar claramente quando um novo recurso enviar dados para terceiros.

## Incident Response

Para este repositorio, a resposta a incidente e pragmatica: remover segredos locais, invalidar tokens externos eventualmente usados, revisar `config.toml`, limpar `temp_dir` e revalidar binarios/modelos confiaveis. O comando `doctor` e o primeiro passo para triagem operacional.

## Related Resources

- [architecture.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/architecture.md:1)
- [tooling.md](/D:/repositorio/bc-developer/whispr-codex/.context/docs/tooling.md:1)
