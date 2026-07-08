#Requires -Version 5.1
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Version
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppName = "亲戚称呼计算器"
$BuildRoot = Join-Path $Root ".build"
$DistDir = Join-Path $BuildRoot "dist"
$WorkDir = Join-Path $BuildRoot "work"
$SpecDir = Join-Path $BuildRoot "spec"
$ReleaseDir = Join-Path $Root "release"
$ZipName = "$AppName-v$Version.zip"
$ZipPath = Join-Path $ReleaseDir $ZipName

Set-Location $Root

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Ensure-Python {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw "未找到 Python。请先安装 Python 3 并加入 PATH。"
    }
    Write-Host "Python: $($python.Source)"
}

function Ensure-Assets {
    $assets = Join-Path $Root "assets"
    if (-not (Test-Path $assets)) {
        throw "缺少 assets 目录：$assets"
    }
}

if ($Version -notmatch '^\d+\.\d+\.\d+([\w.-]+)?$') {
    throw "版本号格式无效，请使用如 1.0.0 或 1.0.0-beta"
}

Write-Step "检查环境 (v$Version)"
Ensure-Python
Ensure-Assets

Write-Step "安装打包依赖"
python -m pip install --upgrade pip
python -m pip install -r (Join-Path $Root "requirements.txt") pyinstaller

Write-Step "清理构建目录"
if (Test-Path $BuildRoot) {
    Remove-Item -Recurse -Force $BuildRoot
}
New-Item -ItemType Directory -Path $DistDir, $WorkDir, $SpecDir -Force | Out-Null
if (-not (Test-Path $ReleaseDir)) {
    New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
}

Write-Step "PyInstaller 打包"
$assetsPath = Join-Path $Root "assets"
$mainPath = Join-Path $Root "main.py"
$pyinstallerArgs = @(
    "--noconfirm",
    "--clean",
    "--windowed",
    "--name", $AppName,
    "--distpath", $DistDir,
    "--workpath", $WorkDir,
    "--specpath", $SpecDir,
    "--add-data", "$assetsPath;assets",
    "--hidden-import", "win32com.client",
    $mainPath
)
python -m PyInstaller @pyinstallerArgs

$appDir = Join-Path $DistDir $AppName
$exePath = Join-Path $appDir "$AppName.exe"
if (-not (Test-Path $exePath)) {
    throw "打包失败：未找到 $AppName.exe"
}

Write-Step "生成 zip"
if (Test-Path $ZipPath) {
    Remove-Item -Force $ZipPath
}
Push-Location $appDir
try {
    Compress-Archive -Path * -DestinationPath $ZipPath -CompressionLevel Optimal -Force
} finally {
    Pop-Location
}

Write-Step "完成"
Write-Host "版本:   v$Version"
Write-Host "输出:   $ZipPath"
Write-Host ""
Write-Host "解压 zip 后双击 $AppName.exe 即可运行。" -ForegroundColor Green
