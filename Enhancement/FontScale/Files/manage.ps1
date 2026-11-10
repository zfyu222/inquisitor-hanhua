param(
    [ValidateSet('install','uninstall')][string]$Action = 'install',
    [ValidateSet(0,125,150,200)][int]$Scale = 0,
    [string]$GameRoot = ''
)
$ErrorActionPreference = 'Stop'
function Get-Sha256([string]$Path) {
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    $stream = [System.IO.File]::OpenRead($Path)
    try { return ([System.BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $stream.Dispose(); $algorithm.Dispose() }
}
try {
    $manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'PATCH_MANIFEST.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($Action -eq 'install' -and $Scale -eq 0) {
        Write-Host '请选择字体大小（相对于汉化原有字体）：'
        Write-Host '  1. 125%（放大25%）'
        Write-Host '  2. 150%（放大50%）'
        Write-Host '  3. 200%（放大100%）'
        Write-Host '  4. 恢复100%（卸载字体增强）'
        Write-Host '  0. 取消'
        do { $choice = Read-Host '输入 0、1、2、3 或 4' } while ($choice -notin @('0','1','2','3','4'))
        switch ($choice) {
            '0' { Write-Host '已取消。'; exit 0 }
            '1' { $Scale = 125 }
            '2' { $Scale = 150 }
            '3' { $Scale = 200 }
            '4' { $Action = 'uninstall' }
        }
    }
    if ([string]::IsNullOrWhiteSpace($GameRoot)) {
        if (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'Game/Inquisitor.exe')) { $GameRoot = $PSScriptRoot }
        elseif (Test-Path -LiteralPath (Join-Path $PSScriptRoot '../../../Game/Game/Inquisitor.exe')) { $GameRoot = Join-Path $PSScriptRoot '../../../Game' }
        else { $GameRoot = (Read-Host '输入 Inquisitor 安装根目录（其中包含 Game 文件夹）').Trim().Trim('"') }
    }
    $root = (Resolve-Path -LiteralPath $GameRoot).Path
    $exe = Join-Path $root 'Game/Inquisitor.exe'
    if (!(Test-Path -LiteralPath $exe)) { throw '未找到 Game/Inquisitor.exe。' }
    if (Get-Process -Name Inquisitor -ErrorAction SilentlyContinue) { throw '请先退出 Inquisitor。' }
    $target = Join-Path $root $manifest.target
    $legacy = Join-Path $root $manifest.legacy_target
    $known = @($manifest.options | ForEach-Object { $_.sha256 })
    # Preflight both files before any mutation, including uninstall/migration.
    if ((Test-Path -LiteralPath $target) -and (Get-Sha256 $target) -notin $known) { throw '发现未知的字体增强文件，已停止操作。' }
    if ((Test-Path -LiteralPath $legacy) -and (Get-Sha256 $legacy) -ne $manifest.legacy_sha256) { throw '旧版125%增强文件已改变，已停止操作。' }
    if ($Action -eq 'uninstall') {
        if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target }
        if (Test-Path -LiteralPath $legacy) { Remove-Item -LiteralPath $legacy }
        Write-Host '已恢复100%字体，汉化保留。'
        exit 0
    }
    if ((Get-Sha256 $exe) -ne $manifest.supported_exe_sha256) { throw '游戏版本不受支持。' }
    $chinese = Join-Path $root 'Game/03_zh.dat'
    if (!(Test-Path -LiteralPath $chinese)) { throw '请先安装子非鱼汉化v1.0。' }
    if ((Get-Sha256 $chinese) -ne $manifest.base_chinese_sha256) { throw '当前汉化不是本增强包适用的v1.0。' }
    $option = @($manifest.options | Where-Object { $_.percent -eq $Scale })
    if ($option.Count -ne 1) { throw '字体倍率配置无效。' }
    $source = Join-Path $PSScriptRoot $option[0].payload
    $bytes = [System.IO.File]::ReadAllBytes($source)
    if ((Get-Sha256 $source) -ne $option[0].sha256) { throw '字体载荷校验失败。' }
    # Same-directory replacement keeps the previous scale intact until the new file is ready.
    $temporary = $target + '.' + [Guid]::NewGuid().ToString('N') + '.tmp'
    $backup = $temporary + '.backup'
    try {
        [System.IO.File]::WriteAllBytes($temporary, $bytes)
        if ((Get-Sha256 $temporary) -ne $option[0].sha256) { throw '临时文件校验失败。' }
        if (Test-Path -LiteralPath $target) { [System.IO.File]::Replace($temporary, $target, $backup) }
        else { [System.IO.File]::Move($temporary, $target) }
    } finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary }
        if (Test-Path -LiteralPath $backup) { Remove-Item -LiteralPath $backup }
    }
    if ((Get-Sha256 $target) -ne $option[0].sha256) { throw '安装后校验失败。' }
    if (Test-Path -LiteralPath $legacy) { Remove-Item -LiteralPath $legacy }
    Write-Host ('已安装字体 ' + $Scale + '%。重新运行安装入口可切换倍率。')
    exit 0
} catch {
    Write-Host ('错误：' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
