from __future__ import annotations

import sys
import threading
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox

from glass import (
    apply_acrylic,
    load_background,
    make_glass_panel,
    set_rounded_corners,
    to_photo,
)
from kinship import RELATIVES, calculate
from widgets import GlassButton, GlassCombobox, GlassDisplay

FONT = "Microsoft YaHei UI"


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


ASSETS = app_root() / "assets"
BG_PATH = ASSETS / "bg.png"

TEXT_PRIMARY = "#1A2B3D"
TEXT_SECONDARY = "#3A5068"
TEXT_LABEL = "#344A60"
TEXT_INPUT = "#1A3348"
TEXT_ARROW = "#5A7490"
TEXT_RESULT = "#0B5394"

WIN_MARGIN = 36
CARD_PAD_X = 48
CARD_PAD_TOP = 44
CARD_PAD_BOTTOM = 36
GAP_LABEL = 42
BTN_GAP = 28

INPUT_W, INPUT_H, INPUT_R = 196, 64, 22
RESULT_W = 220
BTN_W, BTN_H, BTN_R = 240, 64, 26
INPUT_FONT = (FONT, 18)
RESULT_FONT = (FONT, 19, "bold")
BTN_FONT = (FONT, 19, "bold")

TITLE_OFF = 44
SUBTITLE_OFF = 82
ROW_OFF = 118
BTN_OFF = ROW_OFF + INPUT_H + BTN_GAP


@dataclass(frozen=True)
class Layout:
    win_w: int
    win_h: int
    card_x: int
    card_y: int
    card_w: int
    card_h: int
    title_y: int
    subtitle_y: int
    row_y: int
    x_a: int
    x_b: int
    x_r: int
    label_de_x: int
    label_jiao_x: int
    btn_x: int
    btn_y: int


def compute_layout() -> Layout:
    row_width = INPUT_W + GAP_LABEL + INPUT_W + GAP_LABEL + RESULT_W
    content_width = max(row_width, BTN_W)
    card_w = content_width + CARD_PAD_X * 2
    card_h = BTN_OFF + BTN_H + CARD_PAD_BOTTOM

    win_w = card_w + WIN_MARGIN * 2
    win_h = card_h + WIN_MARGIN * 2

    card_x = WIN_MARGIN
    card_y = WIN_MARGIN
    row_x = card_x + CARD_PAD_X + (content_width - row_width) // 2
    x_a = row_x
    x_b = x_a + INPUT_W + GAP_LABEL
    x_r = x_b + INPUT_W + GAP_LABEL

    return Layout(
        win_w=win_w,
        win_h=win_h,
        card_x=card_x,
        card_y=card_y,
        card_w=card_w,
        card_h=card_h,
        title_y=card_y + TITLE_OFF,
        subtitle_y=card_y + SUBTITLE_OFF,
        row_y=card_y + ROW_OFF,
        x_a=x_a,
        x_b=x_b,
        x_r=x_r,
        label_de_x=x_a + INPUT_W + GAP_LABEL // 2,
        label_jiao_x=x_b + INPUT_W + GAP_LABEL // 2,
        btn_x=card_x + (card_w - BTN_W) // 2,
        btn_y=card_y + BTN_OFF,
    )


def speak(text: str) -> None:
    try:
        import win32com.client  # type: ignore[import-untyped]

        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        tokens = speaker.GetVoices()
        female_keywords = ("huihui", "xiaoxiao", "xiaoyi", "female", "女")
        for i in range(tokens.Count):
            token = tokens.Item(i)
            desc = token.GetDescription().lower()
            if any(k in desc for k in female_keywords):
                speaker.Voice = token
                break
        speaker.Speak(text)
    except Exception:
        try:
            import pyttsx3  # type: ignore[import-untyped]

            engine = pyttsx3.init()
            for voice in engine.getProperty("voices"):
                name = (voice.name + voice.id).lower()
                if any(k in name for k in ("huihui", "xiaoxiao", "female", "zira")):
                    engine.setProperty("voice", voice.id)
                    break
            engine.say(text)
            engine.runAndWait()
        except Exception as exc:
            messagebox.showwarning("语音", f"无法播放语音：{exc}")


class KinshipApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("亲戚称呼计算器")
        self.resizable(False, False)
        self.configure(bg="#000000")

        self._layout = compute_layout()
        self._photos: list = []
        self._bg = load_background(BG_PATH, self._layout.win_w, self._layout.win_h)

        self.geometry(f"{self._layout.win_w}x{self._layout.win_h}")
        self._build_ui()
        self.update_idletasks()
        self._apply_window_effects()

    def _apply_window_effects(self) -> None:
        hwnd = self.winfo_id()
        apply_acrylic(hwnd, tint_abgr=0xCCF5FAFF)
        set_rounded_corners(hwnd)
        try:
            self.attributes("-alpha", 0.98)
        except tk.TclError:
            pass

    def _keep_photo(self, photo) -> None:
        self._photos.append(photo)

    def _glass_text(self, canvas: tk.Canvas, x: int, y: int, text: str, **kwargs) -> None:
        font_spec = kwargs.pop("font", (FONT, 16))
        fill = kwargs.pop("fill", TEXT_PRIMARY)
        anchor = kwargs.get("anchor", "center")
        canvas.create_text(x, y + 1, text=text, font=font_spec, fill="#FFFFFF", anchor=anchor)
        canvas.create_text(x, y, text=text, font=font_spec, fill=fill, anchor=anchor)

    def _build_ui(self) -> None:
        lay = self._layout
        self.canvas = tk.Canvas(
            self, width=lay.win_w, height=lay.win_h, highlightthickness=0, bd=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        bg_photo = to_photo(self._bg, self)
        self._keep_photo(bg_photo)
        self.canvas.create_image(0, 0, image=bg_photo, anchor="nw")

        card = make_glass_panel(
            self._bg,
            lay.card_x,
            lay.card_y,
            lay.card_w,
            lay.card_h,
            radius=34,
            blur=24,
            frost=0.10,
            highlight_strength=0.78,
        )
        card_photo = to_photo(card, self)
        self._keep_photo(card_photo)
        self.canvas.create_image(lay.card_x, lay.card_y, image=card_photo, anchor="nw")

        self._scene = self._bg.copy()
        self._scene.paste(card, (lay.card_x, lay.card_y), card)

        self._glass_text(
            self.canvas,
            lay.win_w // 2,
            lay.title_y,
            "亲戚称呼计算器",
            font=(FONT, 30, "bold"),
            fill=TEXT_PRIMARY,
        )
        self._glass_text(
            self.canvas,
            lay.win_w // 2,
            lay.subtitle_y,
            "选择两位亲戚，一键推算称呼",
            font=(FONT, 14),
            fill=TEXT_SECONDARY,
        )

        self._glass_text(
            self.canvas,
            lay.label_de_x,
            lay.row_y + INPUT_H // 2,
            "的",
            font=(FONT, 18),
            fill=TEXT_LABEL,
        )
        self._glass_text(
            self.canvas,
            lay.label_jiao_x,
            lay.row_y + INPUT_H // 2,
            "叫",
            font=(FONT, 18),
            fill=TEXT_LABEL,
        )

        self.combo_a = GlassCombobox(
            self.canvas,
            lay.x_a,
            lay.row_y,
            RELATIVES,
            self._scene,
            self._photos,
            width=INPUT_W,
            height=INPUT_H,
            radius=INPUT_R,
            font=INPUT_FONT,
            text_color=TEXT_INPUT,
            arrow_color=TEXT_ARROW,
        )
        self.combo_a.current(0)

        self.combo_b = GlassCombobox(
            self.canvas,
            lay.x_b,
            lay.row_y,
            RELATIVES,
            self._scene,
            self._photos,
            width=INPUT_W,
            height=INPUT_H,
            radius=INPUT_R,
            font=INPUT_FONT,
            text_color=TEXT_INPUT,
            arrow_color=TEXT_ARROW,
        )
        self.combo_b.current(1)

        self.result_var = tk.StringVar(value="——")
        self.result_display = GlassDisplay(
            self.canvas,
            lay.x_r,
            lay.row_y,
            self.result_var,
            self._scene,
            self._photos,
            width=RESULT_W,
            height=INPUT_H,
            radius=INPUT_R,
            font=RESULT_FONT,
            text_color=TEXT_RESULT,
        )

        self.calc_btn = GlassButton(
            self.canvas,
            lay.btn_x,
            lay.btn_y,
            "计算称呼",
            self._on_calculate,
            self._scene,
            self._photos,
            width=BTN_W,
            height=BTN_H,
            radius=BTN_R,
            font=BTN_FONT,
        )

    def _on_calculate(self) -> None:
        a = self.combo_a.get()
        b = self.combo_b.get()
        if not a or not b:
            messagebox.showinfo("提示", "请先选择两个亲戚")
            return
        result = calculate(a, b)
        self.result_var.set(result)
        sentence = f"{a}的{b}叫{result}"
        threading.Thread(target=speak, args=(sentence,), daemon=True).start()


def main() -> None:
    app = KinshipApp()
    app.mainloop()


if __name__ == "__main__":
    main()
