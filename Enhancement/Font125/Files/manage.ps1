param(
    [ValidateSet('install','uninstall')][string]$Action = 'install',
    [string]$GameRoot = ''
)
$ErrorActionPreference = 'Stop'
function Get-Sha256([string]$Path) {
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        return ([System.BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    } finally {
        $stream.Dispose()
        $algorithm.Dispose()
    }
}
try {
    $manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'PATCH_MANIFEST.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace($GameRoot)) {
        if (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'Game/Inquisitor.exe')) {
            $GameRoot = $PSScriptRoot
        } elseif (Test-Path -LiteralPath (Join-Path $PSScriptRoot '../../../Game/Game/Inquisitor.exe')) {
            $GameRoot = Join-Path $PSScriptRoot '../../../Game'
        } else {
            throw 'Extract this package into the Inquisitor installation root, or pass -GameRoot.'
        }
    }
    $gameFolder = Join-Path (Resolve-Path -LiteralPath $GameRoot).Path 'Game'
    $exe = Join-Path $gameFolder 'Inquisitor.exe'
    if (!(Test-Path -LiteralPath $exe)) { throw 'Game/Inquisitor.exe not found.' }
    if (Get-Process -Name Inquisitor -ErrorAction SilentlyContinue) { throw 'Close Inquisitor first.' }
    $target = Join-Path $gameFolder '04_enhancement_font125.dat'
    if (Test-Path -LiteralPath $target) {
        if ((Get-Sha256 $target) -ne $manifest.payload_sha256) {
            throw 'The enhancement file has changed. Refusing to replace or remove it.'
        }
    }
    if ($Action -eq 'uninstall') {
        if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target }
        Write-Host '125% font enhancement removed. Chinese localization preserved.'
        exit 0
    }
    if ((Get-Sha256 $exe) -ne $manifest.supported_exe_sha256) {
        throw 'Unsupported Inquisitor executable version.'
    }
    $chinese = Join-Path $gameFolder '03_zh.dat'
    if (!(Test-Path -LiteralPath $chinese)) { throw 'Install the Chinese v1.0 localization first.' }
    if ((Get-Sha256 $chinese) -ne $manifest.base_chinese_sha256) {
        throw 'This enhancement requires the verified Chinese v1.0 localization.'
    }
    $source = Join-Path $PSScriptRoot 'Game/04_enhancement_font125.dat'
    if ((Get-Sha256 $source) -ne $manifest.payload_sha256) {
        throw 'Enhancement payload checksum mismatch.'
    }
    # A direct extraction into the game root already installs the overlay.
    if (!(Test-Path -LiteralPath $target)) {
        # CreateNew refuses to overwrite a file that appears after the preflight.
        $stream = [System.IO.File]::Open($target, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write)
        try {
            $bytes = [System.IO.File]::ReadAllBytes($source)
            $stream.Write($bytes, 0, $bytes.Length)
        } finally { $stream.Dispose() }
    }
    if ((Get-Sha256 $target) -ne $manifest.payload_sha256) {
        throw 'Installed checksum mismatch.'
    }
    Write-Host '125% font enhancement installed and verified.'
    exit 0
} catch {
    Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
