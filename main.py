"""亲戚称呼模拟器 — Windows desktop app."""

import threading
import tkinter as tk
from tkinter import ttk, messagebox

from kinship import RELATIVES, calculate

# ── Color palette (light blue tones) ──
BG = "#EAF2FA"           # soft sky background
CARD = "#F7FAFE"         # card surface
BORDER = "#C5D9ED"       # soft blue border
TITLE = "#1A5FA8"        # deep blue title
TEXT = "#2C3E50"         # dark slate text
TEXT_MUTED = "#5B7A99"   # connector words
RESULT_BG = "#E8F2FC"    # result highlight
RESULT_FG = "#1565C0"    # result blue
BTN = "#2B7FD4"          # button primary
BTN_HOVER = "#1A6BB8"    # button pressed
BTN_TEXT = "#FFFFFF"

FONT = "Microsoft YaHei UI"


def speak(text: str) -> None:
    """Speak text using Windows SAPI with a female Chinese voice."""
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
        self.title("亲戚称呼模拟器")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._setup_styles()
        self._build_ui()

    def _setup_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Kinship.TCombobox",
            font=(FONT, 16),
            padding=(10, 8),
            fieldbackground="#FFFFFF",
            background="#FFFFFF",
            foreground=TEXT,
            arrowsize=18,
        )
        style.map(
            "Kinship.TCombobox",
            fieldbackground=[("readonly", "#FFFFFF")],
            selectbackground=[("readonly", "#D6E8F7")],
            selectforeground=[("readonly", TEXT)],
        )

    def _build_ui(self) -> None:
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill=tk.BOTH, expand=True, padx=28, pady=28)

        card = tk.Frame(
            outer,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=32,
            pady=28,
        )
        card.pack()

        # decorative top accent bar
        accent = tk.Frame(card, bg=TITLE, height=4)
        accent.pack(fill=tk.X, pady=(0, 20))

        title = tk.Label(
            card,
            text="亲戚称呼模拟器",
            font=(FONT, 28, "bold"),
            fg=TITLE,
            bg=CARD,
        )
        title.pack(pady=(0, 24))

        row = tk.Frame(card, bg=CARD)
        row.pack(pady=8)

        self.combo_a = ttk.Combobox(
            row,
            values=RELATIVES,
            state="readonly",
            width=10,
            style="Kinship.TCombobox",
        )
        self.combo_a.pack(side=tk.LEFT)
        self.combo_a.current(0)

        tk.Label(
            row, text="  的  ", font=(FONT, 16), fg=TEXT_MUTED, bg=CARD
        ).pack(side=tk.LEFT)

        self.combo_b = ttk.Combobox(
            row,
            values=RELATIVES,
            state="readonly",
            width=10,
            style="Kinship.TCombobox",
        )
        self.combo_b.pack(side=tk.LEFT)
        self.combo_b.current(1)

        tk.Label(
            row, text="  叫  ", font=(FONT, 16), fg=TEXT_MUTED, bg=CARD
        ).pack(side=tk.LEFT)

        result_box = tk.Frame(
            row,
            bg=RESULT_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=12,
            pady=6,
        )
        result_box.pack(side=tk.LEFT)

        self.result_var = tk.StringVar(value="——")
        self.result_label = tk.Label(
            result_box,
            textvariable=self.result_var,
            font=(FONT, 18, "bold"),
            fg=RESULT_FG,
            bg=RESULT_BG,
            width=10,
            anchor="w",
        )
        self.result_label.pack()

        btn = tk.Button(
            card,
            text="计算称呼",
            font=(FONT, 17, "bold"),
            width=12,
            command=self._on_calculate,
            bg=BTN,
            fg=BTN_TEXT,
            activebackground=BTN_HOVER,
            activeforeground=BTN_TEXT,
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=10,
            bd=0,
            highlightthickness=0,
        )
        btn.pack(pady=(20, 4))

    def _on_calculate(self) -> None:
        a = self.combo_a.get()
        b = self.combo_b.get()
        if not a or not b:
            messagebox.showinfo("提示", "请先选择两个亲戚")
            return
        result = calculate(a, b)
        self.result_var.set(result)
        threading.Thread(target=speak, args=(result,), daemon=True).start()


def main() -> None:
    app = KinshipApp()
    app.mainloop()


if __name__ == "__main__":
    main()
