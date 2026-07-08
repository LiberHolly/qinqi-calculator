<div align="center">

# 亲戚称呼计算器

**逢年过节必备 · 再也不会叫错亲戚**

[![Platform](https://img.shields.io/badge/platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](#快速开始)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#快速开始)
[![License](https://img.shields.io/github/license/LiberHolly/qinqi-calculator?style=for-the-badge)](LICENSE)

<br>

<img src="assets/screenshot.png" alt="亲戚称呼计算器界面截图" width="720">

<sub>毛玻璃风格界面 · 91 个常见亲属称谓 · 语音朗读整句结果</sub>

<br><br>

[快速开始](#快速开始) ·
[功能特点](#功能特点) ·
[打包](#打包) ·
[下载使用](#下载使用) ·
[项目结构](#项目结构) ·
[开源协议](#开源协议)

</div>

---

## 功能特点

| | |
|:---:|:---|
| **推算称呼** | 选择两位亲戚，得到「A 的 B」该怎么叫 |
| **语音朗读** | 点击计算后朗读整句，如「爸爸的哥哥叫伯伯」 |
| **丰富词库** | 涵盖父母、祖辈、堂表亲、姻亲、孙辈等 91 项 |
| **滚轮下拉** | 选项过多时支持鼠标滚轮浏览 |
| **便携运行** | 可打包为 exe，无需安装 Python |

> **示例**
>
> `爸爸` + `的` + `哥哥` + `叫` → **伯伯**
>
> 语音：**「爸爸的哥哥叫伯伯」**

---

## 快速开始

### 方式一：双击运行（开发）

```bash
git clone https://github.com/LiberHolly/qinqi-calculator.git
cd qinqi-calculator
```

双击 `start.bat`，脚本会自动检查依赖并启动。

### 方式二：命令行

```bash
pip install -r requirements.txt
python main.py
```

**环境要求：** Windows 10 / 11 · Python 3.10+

---

## 打包

将项目打包为 Windows 便携版 zip，用户解压后无需安装 Python 即可运行。

### 环境要求

- Windows 10 / 11
- Python 3.10+（已加入 PATH）
- 可访问 PyPI（脚本会自动安装 `requirements.txt` 与 `pyinstaller`）

### 打包命令

在项目根目录执行，**必须传入版本号**：

```powershell
.\pack.ps1 1.0.0
```

版本号格式：`主版本.次版本.修订号`，可选后缀，例如 `1.0.0-beta`。

若提示脚本执行策略限制：

```powershell
powershell -ExecutionPolicy Bypass -File .\pack.ps1 1.0.0
```

### 打包流程

`pack.ps1` 会自动完成以下步骤：

1. 检查 Python 与 `assets/` 资源目录
2. 安装/更新依赖与 PyInstaller
3. 在 `.build/` 中执行 PyInstaller 打包（中间文件，已 gitignore）
4. 将 exe 及依赖文件压缩为 zip，输出到 `release/`

### 输出产物

| 路径 | 说明 |
|------|------|
| `release/亲戚称呼计算器-v1.0.0.zip` | 可分发压缩包（文件名随版本号变化） |
| `.build/` | 构建缓存，可删除，不会提交到 git |

zip 内为**扁平结构**：解压后 `亲戚称呼计算器.exe` 与依赖文件在同一目录，双击 exe 即可运行。

### 发布到 GitHub Releases（可选）

```powershell
.\pack.ps1 1.0.0
gh release create v1.0.0 release/亲戚称呼计算器-v1.0.0.zip --title "v1.0.0"
```

---

## 下载使用

从 [GitHub Releases](https://github.com/LiberHolly/qinqi-calculator/releases) 下载对应版本的 zip，或自行打包（见上方 [打包](#打包) 章节）。

1. 解压 `亲戚称呼计算器-vX.Y.Z.zip` 到任意目录
2. 双击 **`亲戚称呼计算器.exe`** 启动

无需安装 Python，无需运行 `start.bat`。

---

## 项目结构

```
qinqi-calculator/
├── main.py          # 主窗口与布局
├── kinship.py       # 称谓选项与查表逻辑
├── widgets.py       # 下拉框、按钮等控件
├── glass.py         # 毛玻璃与亚克力效果
├── assets/
│   ├── bg.png       # 壁纸
│   └── screenshot.png
├── start.bat        # 开发启动
├── pack.ps1         # 便携版打包脚本
├── .build/          # 打包中间文件（gitignore）
├── release/         # 打包输出 zip（gitignore）
└── LICENSE
```

---

## 依赖

| 库 | 用途 |
|----|------|
| [Pillow](https://python-pillow.org/) | 图像处理与毛玻璃渲染 |
| [pywin32](https://github.com/mhammond/pywin32) | Windows 系统语音（SAPI） |
| [pyttsx3](https://github.com/nateshmbhat/pyttsx3) | 语音备选方案 |

---

## 说明

- 称谓结果基于常见用法整理，部分地区或语境可能存在差异
- 查不到的组合会显示 **「暂无此称呼」**
- 语音使用系统自带中文 TTS（如 Microsoft Huihui）

---

## 开源协议

本项目采用 **[MIT License](LICENSE)** 开源。

你可以自由用于个人或商业用途：使用、修改、分发、再授权均可，只需保留版权声明和协议全文。

<div align="center">

<sub>如果这个项目帮到了你，欢迎 Star</sub>

</div>
