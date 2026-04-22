# Setup no Windows

## 1. Preparar o Python

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## 2. Compilar o whisper.cpp

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\bootstrap-whispercpp.ps1 -Destination "$env:USERPROFILE\src\whisper.cpp" -EnableVulkan
```

Se voce nao quiser GPU, rode sem `-EnableVulkan`.

## 3. Baixar um modelo

Dentro do repo do `whisper.cpp`:

```powershell
cd "$env:USERPROFILE\src\whisper.cpp\models"
.\download-ggml-model.cmd small
```

Se o build tiver sido feito com Vulkan, o mesmo `whisper-cli.exe` pode usar GPU por padrao e CPU com `--no-gpu`.

## 4. Criar e ajustar config

```powershell
whispr init-config
notepad "$env:APPDATA\whispr\config.toml"
```

Preencha ao menos:

- `whisper_cpp_path`
- `model_path`
- `backend = "cpu"` se o benchmark mostrar CPU mais rapida
- `inject_mode = "auto"` para usar clipboard com fallback
- `show_capture_indicator = true` para manter o overlay visual durante a captura

## 5. Validar

```powershell
whispr doctor
whispr benchmark
```

## 6. Usar

```powershell
whispr run
```

Com outro app em foco, pressione e segure `F9` para ditar.
