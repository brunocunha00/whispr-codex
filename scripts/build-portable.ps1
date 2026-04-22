param(
    [Parameter(Mandatory = $true)]
    [string]$WhisperCliPath,

    [Parameter(Mandatory = $true)]
    [string]$ModelPath,

    [string]$OutputDir = ".\\dist-portable",

    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$resolvedWhisperCli = (Resolve-Path $WhisperCliPath).Path
$resolvedModel = (Resolve-Path $ModelPath).Path
$whisperBinDir = Split-Path -Parent $resolvedWhisperCli
$resolvedOutputDir = [System.IO.Path]::GetFullPath((Join-Path $repoRoot $OutputDir))
$pyinstallerWorkDir = Join-Path $repoRoot "build\pyinstaller"

if ($Clean) {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $resolvedOutputDir
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $pyinstallerWorkDir
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $repoRoot "build\whispr")
}

python -m pip install -e .[build]

$pyinstallerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onedir",
    "--name", "whispr",
    "--distpath", $resolvedOutputDir,
    "--workpath", $pyinstallerWorkDir,
    "--specpath", (Join-Path $repoRoot "build"),
    "--paths", (Join-Path $repoRoot "src"),
    (Join-Path $repoRoot "src\whispr\__main__.py")
)

python @pyinstallerArgs

$bundleRoot = Join-Path $resolvedOutputDir "whispr"
$vendorDir = Join-Path $bundleRoot "vendor\whispercpp"
$modelsDir = Join-Path $bundleRoot "models"
$tempDir = Join-Path $bundleRoot "tmp"

New-Item -ItemType Directory -Force -Path $vendorDir | Out-Null
New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

Copy-Item $resolvedWhisperCli $vendorDir -Force
Get-ChildItem $whisperBinDir -Filter *.dll | Copy-Item -Destination $vendorDir -Force
Copy-Item $resolvedModel $modelsDir -Force
Copy-Item (Join-Path $repoRoot "README.md") $bundleRoot -Force
Copy-Item (Join-Path $repoRoot "docs\windows-setup.md") $bundleRoot -Force

$modelFileName = Split-Path -Leaf $resolvedModel
$configPath = Join-Path $bundleRoot "config.toml"
$configContent = @"
hotkey = "f9"
language = "pt"
backend = "auto"
model_path = "models\\$modelFileName"
whisper_cpp_path = "vendor\\whispercpp\\whisper-cli.exe"
step_ms = 1000
window_ms = 6000
sample_rate = 16000
threads = 6
commit_mode = "stable-prefix"
inject_target = "foreground-window"
inject_mode = "auto"
show_capture_indicator = true
capture_indicator_position = "top-right"
keep_wav_artifacts = false
temp_dir = "tmp"
vad_model_path = ""
"@

[System.IO.File]::WriteAllText(
    $configPath,
    $configContent,
    [System.Text.UTF8Encoding]::new($false)
)

$zipPath = "$bundleRoot.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}
Compress-Archive -Path (Join-Path $bundleRoot "*") -DestinationPath $zipPath

Write-Host ""
Write-Host "Bundle pronto em: $bundleRoot"
Write-Host "Executavel: $(Join-Path $bundleRoot 'whispr.exe')"
Write-Host "Arquivo zip: $zipPath"
