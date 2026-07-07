"""Windows acrylic blur and liquid-glass image helpers."""

from __future__ import annotations

import ctypes
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageTk

# Windows DWM accent / corner constants
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
WCA_ACCENT_POLICY = 19
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2


class ACCENTPOLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_uint),
        ("AnimationId", ctypes.c_int),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.POINTER(ACCENTPOLICY)),
        ("SizeOfData", ctypes.c_size_t),
    ]


def apply_acrylic(hwnd: int, tint_abgr: int = 0xCCF0F8FF) -> None:
    try:
        accent = ACCENTPOLICY()
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.AccentFlags = 2
        accent.GradientColor = tint_abgr
        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = ctypes.sizeof(accent)
        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
    except Exception:
        pass


def set_rounded_corners(hwnd: int) -> None:
    try:
        preference = ctypes.c_int(DWMWCP_ROUND)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(preference),
            ctypes.sizeof(preference),
        )
    except Exception:
        pass


def load_background(path: Path, width: int, height: int) -> Image.Image:
    if path.is_file():
        img = Image.open(path).convert("RGBA")
        img_ratio = img.width / img.height
        win_ratio = width / height
        if img_ratio > win_ratio:
            new_h = height
            new_w = int(height * img_ratio)
        else:
            new_w = width
            new_h = int(width / img_ratio)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - width) // 2
        top = (new_h - height) // 2
        return img.crop((left, top, left + width, top + height))
    return _fallback_background(width, height)


def sample_bg_hex(background: Image.Image, x: int, y: int) -> str:
    """Pick a canvas background color that blends with wallpaper behind a widget."""
    px = max(0, min(background.width - 1, x))
    py = max(0, min(background.height - 1, y))
    r, g, b, *_ = background.getpixel((px, py))
    return f"#{r:02x}{g:02x}{b:02x}"


def _fallback_background(width: int, height: int) -> Image.Image:
    img = Image.new("RGBA", (width, height), (30, 40, 55, 255))
    draw = ImageDraw.Draw(img)
    orbs = [
        (width * 0.25, height * 0.35, 200, (255, 120, 40, 110)),
        (width * 0.7, height * 0.3, 170, (80, 160, 90, 100)),
        (width * 0.5, height * 0.75, 220, (60, 120, 200, 80)),
    ]
    for cx, cy, r, color in orbs:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    return img.filter(ImageFilter.GaussianBlur(10))


def _rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def _apply_mask(image: Image.Image, radius: int) -> Image.Image:
    mask = _rounded_mask(image.size, radius)
    alpha = image.split()[3]
    image.putalpha(ImageChops.multiply(alpha, mask))
    return image


def make_liquid_glass(
    background: Image.Image,
    x: int,
    y: int,
    width: int,
    height: int,
    *,
    radius: int = 22,
    blur: int = 14,
    frost: float = 0.12,
    tint: tuple[int, int, int, int] | None = None,
    highlight_strength: float = 1.0,
    shadow: bool = True,
) -> Image.Image:
    """Render iOS-style liquid glass: refractive blur, rim light, 3D bevel."""
    pad = 6 if shadow else 0
    out_w, out_h = width + pad * 2, height + pad * 2
    result = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))

    if shadow:
        sh = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle(
            (pad + 1, pad + 5, pad + width + 1, pad + height + 5),
            radius=radius,
            fill=(0, 0, 0, 55),
        )
        result = Image.alpha_composite(result, sh.filter(ImageFilter.GaussianBlur(5)))

    bg = background.convert("RGBA")
    x1 = max(0, min(x, bg.width - 1))
    y1 = max(0, min(y, bg.height - 1))
    x2 = max(x1 + 1, min(x + width, bg.width))
    y2 = max(y1 + 1, min(y + height, bg.height))
    region = bg.crop((x1, y1, x2, y2)).resize((width, height), Image.Resampling.LANCZOS)

    # Backdrop blur + slight saturation lift for a lens-like feel
    frosted = region.filter(ImageFilter.GaussianBlur(blur))
    glass = Image.alpha_composite(
        frosted,
        Image.new("RGBA", (width, height), (255, 255, 255, int(255 * frost))),
    )
    if tint:
        glass = Image.alpha_composite(glass, Image.new("RGBA", (width, height), tint))

    # 3D tubular volume — bright crest, darker trough
    volume = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(volume)
    vdraw.rounded_rectangle(
        (2, 2, width - 3, height // 2 + 2),
        radius=max(radius - 2, 6),
        fill=(255, 255, 255, int(85 * highlight_strength)),
    )
    vdraw.rounded_rectangle(
        (4, height // 2, width - 5, height - 4),
        radius=max(radius - 4, 4),
        fill=(0, 0, 0, int(38 * highlight_strength)),
    )
    glass = Image.alpha_composite(glass, volume)

    # Specular streak along top-left edge
    spec = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(spec)
    sdraw.rounded_rectangle(
        (2, 2, width - 4, int(height * 0.42)),
        radius=max(radius - 2, 6),
        fill=(255, 255, 255, int(95 * highlight_strength)),
    )
    sdraw.line([(8, 8), (width // 2, 8)], fill=(255, 255, 255, int(180 * highlight_strength)), width=2)
    glass = Image.alpha_composite(glass, spec)

    # Rim lighting — bright outer edge + soft inner glow
    rim = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(rim)
    rdraw.rounded_rectangle(
        (1, 1, width - 2, height - 2),
        radius=radius,
        outline=(255, 255, 255, int(220 * highlight_strength)),
        width=2,
    )
    rdraw.rounded_rectangle(
        (3, 3, width - 4, height - 4),
        radius=max(radius - 2, 4),
        outline=(255, 255, 255, int(55 * highlight_strength)),
        width=1,
    )
    glass = Image.alpha_composite(glass, rim)

    glass = _apply_mask(glass, radius)
    result.paste(glass, (pad, pad), glass)
    return result


def flatten_glass_tile(
    scene: Image.Image,
    x: int,
    y: int,
    width: int,
    height: int,
    **kwargs,
) -> Image.Image:
    """Composite liquid glass onto the scene so corners show true background pixels."""
    layer = make_liquid_glass(scene, x, y, width, height, **kwargs)
    pad = 6 if kwargs.get("shadow", True) else 0
    sx, sy = max(0, x - pad), max(0, y - pad)
    base = scene.convert("RGBA").crop((sx, sy, sx + layer.width, sy + layer.height))
    if base.size != layer.size:
        base = base.resize(layer.size, Image.Resampling.LANCZOS)
    return Image.alpha_composite(base, layer)


def make_glass_panel(
    background: Image.Image,
    x: int,
    y: int,
    width: int,
    height: int,
    *,
    radius: int = 28,
    blur: int = 20,
    frost: float = 0.16,
    highlight_strength: float = 1.05,
    border: tuple[int, int, int, int] = (255, 255, 255, 170),
) -> Image.Image:
    """Large liquid-glass card panel."""
    _ = border
    return flatten_glass_tile(
        background,
        x,
        y,
        width,
        height,
        radius=radius,
        blur=blur,
        frost=frost,
        highlight_strength=highlight_strength,
        shadow=False,
    )


def make_liquid_glass_button(
    background: Image.Image,
    x: int,
    y: int,
    width: int,
    height: int,
    *,
    radius: int = 24,
    tint: tuple[int, int, int, int] = (0, 122, 255, 95),
    highlight_strength: float = 1.1,
) -> Image.Image:
    """Liquid-glass button with a subtle blue tint."""
    btn = make_liquid_glass(
        background,
        x,
        y,
        width,
        height,
        radius=radius,
        blur=12,
        frost=0.08,
        tint=tint,
        highlight_strength=highlight_strength,
        shadow=True,
    )
    pad = 6
    return btn.crop((pad, pad, pad + width, pad + height))


def to_photo(image: Image.Image, master) -> ImageTk.PhotoImage:
    return ImageTk.PhotoImage(image, master=master)
