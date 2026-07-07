"""Liquid-glass controls drawn directly on a host canvas (no embedded windows)."""

from __future__ import annotations

import tkinter as tk
from PIL import Image

from glass import flatten_glass_tile, to_photo

FONT = "Microsoft YaHei UI"
POPUP_ROW_H = 40
POPUP_VISIBLE_ROWS = 10
POPUP_PAD = 8


class GlassCombobox:
    """Dropdown control rendered as canvas items."""

    def __init__(
        self,
        canvas: tk.Canvas,
        x: int,
        y: int,
        values: list[str],
        background: Image.Image,
        photos: list,
        *,
        width: int = 196,
        height: int = 64,
        radius: int = 22,
        font: tuple[str, int] = (FONT, 18),
        text_color: str = "#1A3348",
        arrow_color: str = "#5A7490",
    ) -> None:
        self.canvas = canvas
        self.x = x
        self.y = y
        self._values = values
        self._background = background
        self._photos = photos
        self._width = width
        self._height = height
        self._radius = radius
        self._font = font
        self._text_color = text_color
        self._arrow_color = arrow_color
        self._tag = f"combo_{id(self)}"
        self._popup: tk.Toplevel | None = None
        self._var = tk.StringVar(value=values[0] if values else "")
        self._var.trace_add("write", lambda *_a: self._sync_text())
        self._draw(hover=False)
        self.canvas.tag_bind(self._tag, "<Button-1>", self._toggle_popup)
        self.canvas.tag_bind(self._tag, "<Enter>", lambda _e: self._draw(hover=True))
        self.canvas.tag_bind(self._tag, "<Leave>", self._on_leave)
        self.canvas.tag_bind(self._tag, "<Enter>", lambda _e: self.canvas.configure(cursor="hand2"))
        self.canvas.tag_bind(self._tag, "<Leave>", lambda _e: self.canvas.configure(cursor=""))

    def _keep(self, photo) -> None:
        self._photos.append(photo)

    def _sync_text(self) -> None:
        if hasattr(self, "_text_id"):
            self.canvas.itemconfig(self._text_id, text=self._var.get())

    def _clear(self) -> None:
        self.canvas.delete(self._tag)

    def _draw(self, *, hover: bool) -> None:
        self._clear()
        surface = flatten_glass_tile(
            self._background,
            self.x,
            self.y,
            self._width,
            self._height,
            radius=self._radius,
            blur=12 if hover else 14,
            frost=0.09 if hover else 0.06,
            highlight_strength=0.82 if hover else 0.68,
            shadow=False,
        )
        photo = to_photo(surface, self.canvas)
        self._keep(photo)
        self.canvas.create_image(self.x, self.y, image=photo, anchor="nw", tags=(self._tag,))
        self._text_id = self.canvas.create_text(
            self.x + (self._width - 24) // 2,
            self.y + self._height // 2,
            text=self._var.get(),
            font=self._font,
            fill=self._text_color,
            anchor="center",
            tags=(self._tag,),
        )
        self.canvas.create_text(
            self.x + self._width - 22,
            self.y + self._height // 2,
            text="▾",
            font=(self._font[0], self._font[1] + 2),
            fill=self._arrow_color,
            anchor="e",
            tags=(self._tag,),
        )

    def _on_leave(self, _event) -> None:
        if self._popup is None or not self._popup.winfo_exists():
            self._draw(hover=False)

    def get(self) -> str:
        return self._var.get()

    def current(self, index: int | None = None) -> int | None:
        if index is None:
            try:
                return self._values.index(self._var.get())
            except ValueError:
                return 0
        if 0 <= index < len(self._values):
            self._var.set(self._values[index])
        return index

    def _toggle_popup(self, _event) -> None:
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
            self._popup = None
            return
        self._open_popup()

    def _open_popup(self) -> None:
        row_h = POPUP_ROW_H
        pad = POPUP_PAD
        content_h = len(self._values) * row_h + pad * 2
        visible_rows = min(POPUP_VISIBLE_ROWS, len(self._values))
        viewport_h = visible_rows * row_h + pad * 2
        scrollable = content_h > viewport_h

        popup = tk.Toplevel(self.canvas)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.update_idletasks()
        popup_x = self.canvas.winfo_rootx() + self.x
        popup_y = self.canvas.winfo_rooty() + self.y + self._height + 6
        popup.geometry(f"{self._width}x{viewport_h}+{popup_x}+{popup_y}")
        self._popup = popup

        shell = tk.Canvas(
            popup,
            width=self._width,
            height=viewport_h,
            highlightthickness=0,
            bd=0,
            bg="#010101",
        )
        shell.pack(fill=tk.BOTH, expand=True)
        try:
            popup.attributes("-transparentcolor", "#010101")
        except tk.TclError:
            pass

        # Fixed viewport-sized panel keeps rounded corners while only items scroll.
        panel = flatten_glass_tile(
            self._background,
            self.x,
            self.y + self._height,
            self._width,
            viewport_h,
            radius=self._radius,
            blur=16,
            frost=0.12,
            highlight_strength=0.75,
            shadow=False,
        )
        panel_photo = to_photo(panel, shell)
        bg_id = shell.create_image(0, 0, image=panel_photo, anchor="nw", tags=("popup_bg",))
        shell._panel_photo = panel_photo

        shell.configure(scrollregion=(0, 0, self._width, content_h))
        if scrollable:
            shell.configure(yscrollincrement=row_h)

        def pin_bg() -> None:
            shell.coords(bg_id, 0, shell.canvasy(0))
            shell.tag_lower("popup_bg")

        def on_pick(_e=None, val: str = "") -> None:
            self._var.set(val)
            popup.destroy()
            self._popup = None
            self._draw(hover=False)

        for i, value in enumerate(self._values):
            item_y = pad + i * row_h + row_h // 2
            text_id = shell.create_text(
                self._width // 2,
                item_y,
                text=value,
                font=self._font,
                fill=self._text_color,
                anchor="center",
                tags=("popup_item",),
            )

            def bind_pick(_e=None, val: str = value) -> None:
                on_pick(val=val)

            shell.tag_bind(text_id, "<Button-1>", bind_pick)
            shell.tag_bind(text_id, "<Enter>", lambda _e, tid=text_id: (
                shell.itemconfig(tid, fill="#0B5394"),
                shell.configure(cursor="hand2"),
            ))
            shell.tag_bind(text_id, "<Leave>", lambda _e, tid=text_id: shell.itemconfig(
                tid, fill=self._text_color
            ))

        def on_wheel(event: tk.Event) -> None:
            if not scrollable:
                return "break"
            delta = -1 * (event.delta // 120) if event.delta else 0
            if delta == 0:
                delta = -1 if event.num == 4 else 1 if event.num == 5 else 0
            shell.yview_scroll(delta, "units")
            pin_bg()
            return "break"

        if scrollable:
            for widget in (popup, shell):
                widget.bind("<MouseWheel>", on_wheel)
                widget.bind("<Button-4>", on_wheel)
                widget.bind("<Button-5>", on_wheel)
            shell.tag_bind("popup_item", "<MouseWheel>", on_wheel)
            shell.tag_bind("popup_item", "<Button-4>", on_wheel)
            shell.tag_bind("popup_item", "<Button-5>", on_wheel)
            shell.bind("<Enter>", lambda _e: shell.focus_set())

        popup.bind("<Escape>", lambda _e: (popup.destroy(), setattr(self, "_popup", None)))
        shell.focus_set()
        pin_bg()


class GlassDisplay:
    """Read-only result field drawn on canvas."""

    def __init__(
        self,
        canvas: tk.Canvas,
        x: int,
        y: int,
        textvariable: tk.StringVar,
        background: Image.Image,
        photos: list,
        *,
        width: int = 220,
        height: int = 64,
        radius: int = 22,
        font: tuple[str, int, str] = (FONT, 19, "bold"),
        text_color: str = "#0B5394",
    ) -> None:
        self.canvas = canvas
        self._tag = f"display_{id(self)}"
        surface = flatten_glass_tile(
            background,
            x,
            y,
            width,
            height,
            radius=radius,
            blur=14,
            frost=0.06,
            tint=(11, 83, 148, 18),
            highlight_strength=0.72,
            shadow=False,
        )
        photo = to_photo(surface, canvas)
        photos.append(photo)
        canvas.create_image(x, y, image=photo, anchor="nw", tags=(self._tag,))
        self._text_id = canvas.create_text(
            x + width // 2,
            y + height // 2,
            text=textvariable.get(),
            font=font,
            fill=text_color,
            anchor="center",
            tags=(self._tag,),
        )
        textvariable.trace_add(
            "write",
            lambda *_a: canvas.itemconfig(self._text_id, text=textvariable.get()),
        )


class GlassButton:
    """Rounded liquid-glass button drawn on canvas."""

    def __init__(
        self,
        canvas: tk.Canvas,
        x: int,
        y: int,
        text: str,
        command,
        background: Image.Image,
        photos: list,
        *,
        width: int = 240,
        height: int = 64,
        radius: int = 26,
        font: tuple[str, int, str] = (FONT, 19, "bold"),
        text_color: str = "#FFFFFF",
    ) -> None:
        self.canvas = canvas
        self.x = x
        self.y = y
        self._command = command
        self._background = background
        self._photos = photos
        self._width = width
        self._height = height
        self._radius = radius
        self._text = text
        self._font = font
        self._text_color = text_color
        self._tag = f"btn_{id(self)}"
        self._normal = self._render(hover=False)
        self._hover = self._render(hover=True)
        self._img_id = canvas.create_image(x, y, image=self._normal, anchor="nw", tags=(self._tag,))
        canvas.create_text(
            x + width // 2,
            y + height // 2,
            text=text,
            fill=text_color,
            font=font,
            tags=(self._tag,),
        )
        canvas.tag_bind(self._tag, "<Enter>", lambda _e: (
            canvas.itemconfig(self._img_id, image=self._hover),
            canvas.configure(cursor="hand2"),
        ))
        canvas.tag_bind(self._tag, "<Leave>", lambda _e: (
            canvas.itemconfig(self._img_id, image=self._normal),
            canvas.configure(cursor=""),
        ))
        canvas.tag_bind(self._tag, "<Button-1>", lambda _e: command())

    def _render(self, *, hover: bool):
        tint = (0, 90, 200, 80 if hover else 65)
        surface = flatten_glass_tile(
            self._background,
            self.x,
            self.y,
            self._width,
            self._height,
            radius=self._radius,
            blur=10 if hover else 12,
            frost=0.05,
            tint=tint,
            highlight_strength=0.88 if hover else 0.72,
            shadow=False,
        )
        photo = to_photo(surface, self.canvas)
        self._photos.append(photo)
        return photo
