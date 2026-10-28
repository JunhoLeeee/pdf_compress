"""PDF 압축기 GUI: PDF 파일(또는 폴더)을 창에 끌어다 놓으면 같은 폴더에 압축본을 만든다.

실행 파일 아이콘 위에 PDF를 끌어다 놓아도 동작한다 (명령행 인자로 전달됨).
"""
import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from tkinterdnd2 import DND_FILES, TkinterDnD

from compressor import DEFAULT_LEVEL, LEVELS, collect_pdfs, compress, human


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.jobs: queue.Queue = queue.Queue()
        self.events: queue.Queue = queue.Queue()
        self.pending = 0

        root.title("PDF 압축기")
        icon = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "assets" / "icon_256.png"
        if icon.exists():
            self.icon = tk.PhotoImage(file=str(icon))
            root.iconphoto(True, self.icon)
        root.geometry("560x440")
        root.minsize(420, 340)

        top = ttk.Frame(root, padding=(12, 10, 12, 0))
        top.pack(fill="x")
        ttk.Label(top, text="압축 강도:").pack(side="left")
        self.level = tk.StringVar(value=DEFAULT_LEVEL)
        for name in LEVELS:
            ttk.Radiobutton(top, text=name, value=name, variable=self.level).pack(side="left", padx=4)

        self.drop = tk.Label(
            root,
            text="여기에 PDF 파일이나 폴더를 끌어다 놓으세요\n(클릭하면 파일 선택)",
            relief="groove", bd=2, height=6, bg="#f2f4f7", fg="#333",
            font=("TkDefaultFont", 13),
        )
        self.drop.pack(fill="x", padx=12, pady=10)
        self.drop.drop_target_register(DND_FILES)
        self.drop.dnd_bind("<<DropEnter>>", lambda e: self._highlight(True))
        self.drop.dnd_bind("<<DropLeave>>", lambda e: self._highlight(False))
        self.drop.dnd_bind("<<Drop>>", self._on_drop)
        self.drop.bind("<Button-1>", self._on_click)

        self.status = tk.StringVar(value="대기 중")
        ttk.Label(root, textvariable=self.status, padding=(12, 0)).pack(anchor="w")

        frame = ttk.Frame(root, padding=(12, 4, 12, 12))
        frame.pack(fill="both", expand=True)
        self.log = tk.Text(frame, height=10, state="disabled", wrap="word")
        scroll = ttk.Scrollbar(frame, command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log.pack(side="left", fill="both", expand=True)

        threading.Thread(target=self._worker, daemon=True).start()
        root.after(100, self._poll)

    def _highlight(self, on: bool):
        self.drop.configure(bg="#dbe8ff" if on else "#f2f4f7")
        return "copy"

    def _on_drop(self, event):
        self._highlight(False)
        self.add(self.root.tk.splitlist(event.data))
        return "copy"

    def _on_click(self, _event):
        files = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf"), ("모든 파일", "*.*")])
        if files:
            self.add(files)

    def add(self, paths):
        pdfs = collect_pdfs(paths)
        if not pdfs:
            self._write("PDF 파일이 없습니다.")
            return
        for p in pdfs:
            self.jobs.put((p, self.level.get()))
        self.pending += len(pdfs)
        self.status.set(f"압축 중… 남은 파일 {self.pending}개")

    def _worker(self):
        while True:
            path, level = self.jobs.get()
            self.events.put(("start", path))
            try:
                self.events.put(("done", compress(path, level)))
            except Exception as e:  # 손상된 PDF 등
                self.events.put(("error", (path, e)))

    def _poll(self):
        while not self.events.empty():
            kind, data = self.events.get()
            if kind == "start":
                self.status.set(f"압축 중: {data.name} (남은 파일 {self.pending}개)")
                continue
            self.pending -= 1
            if kind == "error":
                path, err = data
                self._write(f"✗ {path.name}: 실패 - {err}")
            elif data.out:
                self._write(
                    f"✓ {data.src.name} → {data.out.name}\n"
                    f"   {human(data.before)} → {human(data.after)} ({data.ratio:.0f}% 감소)"
                )
            else:
                self._write(f"- {data.src.name}: {data.message}")
            if self.pending == 0:
                self.status.set("모든 작업 완료")
        self.root.after(100, self._poll)

    def _write(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")


def run_droplet(paths):
    """아이콘에 끌어다 놓은 파일을 창 없이 바로 압축하고, 결과 알림을 잠깐 띄운 뒤 종료."""
    pdfs = collect_pdfs(paths)
    lines, saved = [], 0
    for p in pdfs:
        try:
            r = compress(p, DEFAULT_LEVEL)
        except Exception as e:
            lines.append(f"✗ {p.name}: 실패 - {e}")
            continue
        if r.out:
            saved += r.before - r.after
            lines.append(f"✓ {p.name}  {human(r.before)} → {human(r.after)} ({r.ratio:.0f}%↓)")
        else:
            lines.append(f"- {p.name}: {r.message}")
    if not pdfs:
        lines.append("PDF 파일이 없습니다.")
    elif saved:
        lines.append(f"\n총 {human(saved)} 절약 · 원본과 같은 폴더에 저장됨")
    toast("PDF 압축 완료", "\n".join(lines[-12:]))


def toast(title: str, text: str, seconds: int = 4):
    """화면 우측 상단에 잠깐 떴다가 사라지는 알림 (클릭하면 즉시 닫힘)."""
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    frame = tk.Frame(root, bg="#222", padx=16, pady=12)
    frame.pack()
    tk.Label(frame, text=title, bg="#222", fg="white", font=("TkDefaultFont", 13, "bold")).pack(anchor="w")
    tk.Label(frame, text=text, bg="#222", fg="#ddd", justify="left").pack(anchor="w", pady=(4, 0))
    root.update_idletasks()
    x = root.winfo_screenwidth() - root.winfo_reqwidth() - 24
    root.geometry(f"+{x}+48")
    for w in (root, frame, *frame.winfo_children()):
        w.bind("<Button-1>", lambda e: root.destroy())
    root.after(seconds * 1000, root.destroy)
    root.mainloop()


def main():
    # 실행 파일 아이콘에 PDF를 끌어다 놓은 경우 → 창 없이 바로 압축
    # (macOS .app 은 빌드 시 argv_emulation 으로 드롭한 파일이 sys.argv 로 들어온다)
    if len(sys.argv) > 1:
        run_droplet(sys.argv[1:])
        return
    # 그냥 실행한 경우 → 드래그앤드롭 창
    root = TkinterDnD.Tk()
    app = App(root)
    root.createcommand("::tk::mac::OpenDocument", lambda *paths: app.add(paths))
    root.mainloop()


if __name__ == "__main__":
    main()
