param(
    [Parameter(Mandatory = $true)]
    [string]$WhisperCliPath,

    [Parameter(Mandatory = $true)]
    [string]$ModelPath,

    [string]$FfmpegPath,

    [string]$OutputDir = ".\\dist-portable",

    [switch]$SingleFile,

    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$resolvedWhisperCli = (Resolve-Path $WhisperCliPath).Path
$resolvedModel = (Resolve-Path $ModelPath).Path
$whisperBinDir = Split-Path -Parent $resolvedWhisperCli
$resolvedFfmpeg = $null
$ffmpegBinDir = $null
if ($FfmpegPath) {
    $resolvedFfmpeg = (Resolve-Path $FfmpegPath).Path
    $ffmpegBinDir = Split-Path -Parent $resolvedFfmpeg
}
$resolvedOutputDir = [System.IO.Path]::GetFullPath((Join-Path $repoRoot $OutputDir))
$pyinstallerWorkDir = Join-Path $repoRoot "build\pyinstaller"
$specPath = Join-Path $repoRoot "build"

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
    "--name", "whispr",
    "--distpath", $resolvedOutputDir,
    "--workpath", $pyinstallerWorkDir,
    "--specpath", $specPath,
    "--paths", (Join-Path $repoRoot "src"),
    (Join-Path $repoRoot "src\whispr\__main__.py")
)

if ($SingleFile) {
    $pyinstallerArgs += "--onefile"
    $pyinstallerArgs += @("--add-binary", "$resolvedWhisperCli;vendor/whispercpp")
    Get-ChildItem $whisperBinDir -Filter *.dll | ForEach-Object {
        $pyinstallerArgs += @("--add-binary", "$($_.FullName);vendor/whispercpp")
    }
    if ($resolvedFfmpeg) {
        $pyinstallerArgs += @("--add-binary", "$resolvedFfmpeg;vendor/ffmpeg")
        Get-ChildItem $ffmpegBinDir -Filter *.dll | ForEach-Object {
            $pyinstallerArgs += @("--add-binary", "$($_.FullName);vendor/ffmpeg")
        }
    }
    $pyinstallerArgs += @("--add-data", "$resolvedModel;models")
} else {
    $pyinstallerArgs += "--onedir"
}

python @pyinstallerArgs

$modelFileName = Split-Path -Leaf $resolvedModel
$ffmpegConfigPath = ""
if ($resolvedFfmpeg) {
    $ffmpegExeName = Split-Path -Leaf $resolvedFfmpeg
    $ffmpegConfigPath = "vendor\\ffmpeg\\$ffmpegExeName"
}
$bundleRoot = Join-Path $resolvedOutputDir "whispr"
$bundleExePath = if ($SingleFile) {
    "$bundleRoot.exe"
} else {
    Join-Path $bundleRoot "whispr.exe"
}
$configDir = if ($SingleFile) {
    $resolvedOutputDir
} else {
    $bundleRoot
}
$configPath = Join-Path $configDir "config.toml"
$configContent = @"
hotkey = "f9"
language = "pt"
backend = "auto"
model_path = "models\\$modelFileName"
whisper_cpp_path = "vendor\\whispercpp\\whisper-cli.exe"
ffmpeg_path = "$ffmpegConfigPath"
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
telegram_bot_token = ""
telegram_allowed_chat_ids = []
telegram_poll_timeout_s = 30
telegram_api_base_url = "https://api.telegram.org"
"@

if (-not $SingleFile) {
    $vendorDir = Join-Path $bundleRoot "vendor\whispercpp"
    $ffmpegVendorDir = Join-Path $bundleRoot "vendor\ffmpeg"
    $modelsDir = Join-Path $bundleRoot "models"
    $tempDir = Join-Path $bundleRoot "tmp"

    New-Item -ItemType Directory -Force -Path $vendorDir | Out-Null
    New-Item -ItemType Directory -Force -Path $ffmpegVendorDir | Out-Null
    New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

    Copy-Item $resolvedWhisperCli $vendorDir -Force
    Get-ChildItem $whisperBinDir -Filter *.dll | Copy-Item -Destination $vendorDir -Force
    if ($resolvedFfmpeg) {
        Copy-Item $resolvedFfmpeg $ffmpegVendorDir -Force
        Get-ChildItem $ffmpegBinDir -Filter *.dll | Copy-Item -Destination $ffmpegVendorDir -Force
    }
    Copy-Item $resolvedModel $modelsDir -Force
    Copy-Item (Join-Path $repoRoot "README.md") $bundleRoot -Force
    Copy-Item (Join-Path $repoRoot "docs\windows-setup.md") $bundleRoot -Force
}

[System.IO.File]::WriteAllText(
    $configPath,
    $configContent,
    [System.Text.UTF8Encoding]::new($false)
)

$zipPath = if ($SingleFile) {
    Join-Path $resolvedOutputDir "whispr-singlefile.zip"
} else {
    "$bundleRoot.zip"
}
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}
if ($SingleFile) {
    Compress-Archive -Path $bundleExePath, $configPath -DestinationPath $zipPath
} else {
    Compress-Archive -Path (Join-Path $bundleRoot "*") -DestinationPath $zipPath
}

Write-Host ""
if ($SingleFile) {
    Write-Host "Build single-file pronto."
    Write-Host "Executavel: $bundleExePath"
    Write-Host "Config inicial: $configPath"
    if ($resolvedFfmpeg) {
        Write-Host "ffmpeg embutido dentro do executavel."
    }
    Write-Host "Modelo e whisper-cli embutidos dentro do executavel."
} else {
    Write-Host "Bundle pronto em: $bundleRoot"
    Write-Host "Executavel: $(Join-Path $bundleRoot 'whispr.exe')"
    if ($resolvedFfmpeg) {
        Write-Host "ffmpeg incluido em: $(Join-Path $ffmpegVendorDir (Split-Path -Leaf $resolvedFfmpeg))"
    }
}
Write-Host "Arquivo zip: $zipPath"
