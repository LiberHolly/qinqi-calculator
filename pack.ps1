#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReleaseDir = Join-Path $Root "release"
$PortableDir = Join-Path $ReleaseDir "portable"
$BuildDir = Join-Path $ReleaseDir "build"
$AppName = "亲戚称呼计算器"
$ZipName = "$AppName-portable.zip"
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

Write-Step "检查环境"
Ensure-Python
Ensure-Assets

Write-Step "安装打包依赖"
python -m pip install --upgrade pip
python -m pip install -r (Join-Path $Root "requirements.txt") pyinstaller

Write-Step "清理旧输出"
if (Test-Path $ReleaseDir) {
    Remove-Item -Recurse -Force $ReleaseDir
}
New-Item -ItemType Directory -Path $PortableDir -Force | Out-Null
New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null

Write-Step "PyInstaller 打包"
$assetsPath = Join-Path $Root "assets"
$mainPath = Join-Path $Root "main.py"
$pyinstallerArgs = @(
    "--noconfirm",
    "--clean",
    "--windowed",
    "--name", $AppName,
    "--distpath", $PortableDir,
    "--workpath", $BuildDir,
    "--specpath", $ReleaseDir,
    "--add-data", "$assetsPath;assets",
    "--hidden-import", "win32com.client",
    $mainPath
)
python -m PyInstaller @pyinstallerArgs

$appDir = Join-Path $PortableDir $AppName
if (-not (Test-Path (Join-Path $appDir "$AppName.exe"))) {
    throw "打包失败：未找到 $AppName.exe"
}

Write-Step "生成 zip"
if (Test-Path $ZipPath) {
    Remove-Item -Force $ZipPath
}
Compress-Archive -Path $appDir -DestinationPath $ZipPath -Force

Write-Step "完成"
Write-Host "便携版文件夹: $appDir"
Write-Host "便携版 zip:     $ZipPath"
