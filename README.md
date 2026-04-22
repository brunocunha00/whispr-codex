# whispr-codex

CLI de ditado local para Windows com captura por hotkey global, transcricao incremental e insercao do texto na janela em foco.

## O que ele faz

- Roda via terminal com `whispr run`.
- Inicia captura enquanto a hotkey estiver pressionada.
- Transcreve em janelas deslizantes usando `whisper.cpp` com modelos `Whisper` da OpenAI executados localmente.
- Digita apenas o prefixo estabilizado na janela em foco, evitando apagar texto ja enviado.
- Permite `backend = auto | vulkan | cpu` para tentar GPU primeiro e cair para CPU.
- Permite `inject_mode = auto | clipboard | sendinput` para controlar como o texto entra no app focado.
- Mostra um indicador visual sempre-no-topo enquanto a captura estiver ativa.

## Escolha tecnica

- Modelo base: `Whisper`, open source da OpenAI.
- Inferencia local: `whisper.cpp`.
- GPU em Windows para placas AMD antigas: `best effort` via build com `GGML_VULKAN=1`.
- Fallback obrigatorio: `--no-gpu`, mantendo a aplicacao funcional em CPU.

## Requisitos

- Windows 10/11
- Python 3.13+
- CMake 3.27+
- Visual Studio Build Tools ou MSVC equivalente
- Driver de video com suporte a Vulkan se quiser tentar GPU

## Instalacao do projeto

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Bootstrap do whisper.cpp

O projeto nao embute o `whisper.cpp`. Ele usa o executavel `whisper-cli.exe` que voce compila localmente.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\bootstrap-whispercpp.ps1 -Destination "$env:USERPROFILE\src\whisper.cpp" -EnableVulkan
```

Depois baixe um modelo `ggml`, por exemplo `ggml-small.bin`, e aponte o caminho no config:

```powershell
whispr init-config
notepad "$env:APPDATA\whispr\config.toml"
```

## Fluxo rapido

1. Rode `whispr doctor` para validar microfone, hotkey, modelo e `whisper-cli`.
2. Ajuste `whisper_cpp_path` e `model_path` no config.
3. Execute `whispr benchmark` para comparar `vulkan` e `cpu`.
4. Execute `whispr run`.
5. Mantenha `F9` pressionado para ditar no app com foco.

## Build Portatil

Para gerar uma pasta pronta para copiar para outra maquina Windows x64:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\build-portable.ps1 `
  -WhisperCliPath "D:\repositorio\bc-developer\whisper.cpp\build\bin\Release\whisper-cli.exe" `
  -ModelPath "D:\repositorio\bc-developer\whisper.cpp\models\ggml-small.bin" `
  -Clean
```

Saida esperada:

- `dist-portable\whispr\whispr.exe`
- `dist-portable\whispr\vendor\whispercpp\*.dll`
- `dist-portable\whispr\models\ggml-small.bin`
- `dist-portable\whispr\config.toml`
- `dist-portable\whispr.zip`

Na outra maquina, extraia a pasta ou zip e rode `whispr.exe`. Nessa modalidade, o app usa o `config.toml` ao lado do executavel e resolve caminhos relativos sem depender de `%APPDATA%`.

## Comandos

```text
whispr init-config   Cria o config padrao em %APPDATA%\whispr\config.toml
whispr doctor        Verifica ambiente, caminhos e dependencias opcionais
whispr devices       Lista dispositivos de entrada de audio
whispr benchmark     Compara CPU e GPU com um sample sintetico
whispr run           Inicia o loop de ditado
```

## Configuracao

Arquivo padrao: `%APPDATA%\whispr\config.toml`

```toml
hotkey = "f9"
language = "pt"
backend = "auto"
model_path = "C:\\Users\\you\\AppData\\Roaming\\whispr\\models\\ggml-small.bin"
whisper_cpp_path = "C:\\Users\\you\\src\\whisper.cpp\\build\\bin\\Release\\whisper-cli.exe"
step_ms = 1000
window_ms = 6000
sample_rate = 16000
threads = 8
commit_mode = "stable-prefix"
inject_target = "foreground-window"
inject_mode = "auto"
show_capture_indicator = true
capture_indicator_position = "top-right"
keep_wav_artifacts = false
temp_dir = "C:\\Users\\you\\AppData\\Roaming\\whispr\\tmp"
vad_model_path = ""
```

## Observacoes

- O `RX 580` nao tem caminho oficial forte via ROCm no Windows; por isso o projeto tenta `Vulkan` e faz fallback.
- O texto e inserido no app em foco de teclado, nao na posicao do mouse.
- `inject_mode = "auto"` usa `clipboard + Ctrl+V` e restaura o clipboard anterior; se isso falhar, cai para `SendInput`.
- `show_capture_indicator = true` exibe um ponto vermelho com `REC` enquanto a hotkey estiver pressionada.
- A v1 nao faz `backspace` em texto ja digitado para evitar efeitos colaterais em apps de terceiros.

## Referencias

- OpenAI Whisper: https://openai.com/index/whisper/
- Repositorio Whisper: https://github.com/openai/whisper
- whisper.cpp: https://github.com/ggml-org/whisper.cpp
- Compatibilidade Radeon/ROCm Windows: https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/compatibility/compatibilityrad/windows/windows_compatibility.html
