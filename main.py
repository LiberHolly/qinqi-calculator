"""亲戚称呼模拟器 — Windows desktop app."""

import threading
import tkinter as tk
from tkinter import ttk, messagebox

from kinship import RELATIVES, calculate


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
        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 6}

        title = tk.Label(
            self,
            text="亲戚称呼模拟器",
            font=("Microsoft YaHei UI", 22, "bold"),
        )
        title.pack(pady=(20, 16))

        row = tk.Frame(self)
        row.pack(padx=24, pady=8)

        self.combo_a = ttk.Combobox(
            row, values=RELATIVES, state="readonly", width=8, font=("Microsoft YaHei UI", 12)
        )
        self.combo_a.pack(side=tk.LEFT)
        self.combo_a.current(0)

        tk.Label(row, text="  的  ", font=("Microsoft YaHei UI", 12)).pack(side=tk.LEFT)

        self.combo_b = ttk.Combobox(
            row, values=RELATIVES, state="readonly", width=8, font=("Microsoft YaHei UI", 12)
        )
        self.combo_b.pack(side=tk.LEFT)
        self.combo_b.current(1)

        tk.Label(row, text="  叫  ", font=("Microsoft YaHei UI", 12)).pack(side=tk.LEFT)

        self.result_var = tk.StringVar(value="——")
        self.result_label = tk.Label(
            row,
            textvariable=self.result_var,
            font=("Microsoft YaHei UI", 14, "bold"),
            fg="#c0392b",
            width=12,
            anchor="w",
        )
        self.result_label.pack(side=tk.LEFT)

        btn = tk.Button(
            self,
            text="计算称呼",
            font=("Microsoft YaHei UI", 13),
            width=14,
            command=self._on_calculate,
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
        )
        btn.pack(pady=(12, 24))

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
