param(
    [Parameter(Mandatory = $true)]
    [string]$Destination,

    [switch]$EnableVulkan
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git nao encontrado no PATH."
}

if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
    throw "cmake nao encontrado no PATH."
}

$destinationPath = [System.IO.Path]::GetFullPath($Destination)

if (-not (Test-Path -LiteralPath $destinationPath)) {
    git clone https://github.com/ggml-org/whisper.cpp.git $destinationPath
}

Push-Location $destinationPath
try {
    git pull --ff-only

    $buildArgs = @("-B", "build")
    if ($EnableVulkan) {
        $buildArgs += "-DGGML_VULKAN=1"
    }

    & cmake @buildArgs
    & cmake --build build -j --config Release

    Write-Host ""
    Write-Host "Build concluido."
    Write-Host "Executavel esperado:"
    Write-Host "  $destinationPath\build\bin\Release\whisper-cli.exe"
}
finally {
    Pop-Location
}
