from __future__ import annotations

import argparse
import tkinter as tk
from datetime import date
from tkinter import messagebox


from reminder_state import ReminderState


SNOOZE_MINUTES = 10
SNOOZE_MS = SNOOZE_MINUTES * 60 * 1000
RAISE_INTERVAL_MS = 3000


def window_policy() -> dict[str, object]:
    return {
        "force_center": True,
        "remove_window_chrome": True,
        "topmost": True,
        "content_fills_window": True,
        "window_background": "#ffffff",
        "raise_interval_ms": RAISE_INTERVAL_MS,
    }


def should_restore_on_unmap(is_snoozing: bool) -> bool:
    return not is_snoozing


def should_force_visible(is_snoozing: bool) -> bool:
    return not is_snoozing


class ReminderApp:
    def __init__(self, root: tk.Tk, task: str, state: ReminderState | None = None) -> None:
        self.root = root
        self.state = state or ReminderState()
        self.local_date = date.today()
        self.task = task
        self.snooze_job: str | None = None
        self.is_snoozing = False

        self.root.title("每日任务提醒")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_blocked_close)
        self.root.configure(bg="#ffffff")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.attributes("-topmost", True)
        self.root.bind("<Unmap>", self.on_unmap)

        self.build_ui()
        self.center_window()
        self.keep_on_top()

    def build_ui(self) -> None:
        frame = tk.Frame(self.root, bg="#ffffff", padx=28, pady=24)
        frame.grid(row=0, column=0, sticky="nsew")

        title = tk.Label(
            frame,
            text=f"今日任务：{self.task}",
            bg="#ffffff",
            fg="#171f2d",
            font=("Microsoft YaHei UI", 20, "bold"),
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w")

        rule_text = f"本地日期：{self.local_date.isoformat()}"
        rule = tk.Label(
            frame,
            text=rule_text,
            bg="#ffffff",
            fg="#5d6878",
            font=("Microsoft YaHei UI", 10),
            wraplength=390,
            justify="left",
        )
        rule.grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 18))

        target = tk.Label(
            frame,
            text=f"未确认：{self.task}",
            bg="#fff5f2",
            fg="#b9442f",
            font=("Microsoft YaHei UI", 14, "bold"),
            padx=16,
            pady=12,
        )
        target.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 18))

        confirm = tk.Button(
            frame,
            text=f"已完成：{self.task}",
            command=self.confirm,
            bg="#1f7a63",
            fg="#ffffff",
            activebackground="#17624f",
            activeforeground="#ffffff",
            relief="flat",
            font=("Microsoft YaHei UI", 12, "bold"),
            padx=14,
            pady=10,
        )
        confirm.grid(row=3, column=0, sticky="ew", padx=(0, 10))

        snooze = tk.Button(
            frame,
            text=f"{SNOOZE_MINUTES} 分钟后再提醒",
            command=self.snooze,
            bg="#ffffff",
            fg="#171f2d",
            activebackground="#f1f4f7",
            relief="solid",
            bd=1,
            font=("Microsoft YaHei UI", 11, "bold"),
            padx=12,
            pady=10,
        )
        snooze.grid(row=3, column=1, sticky="ew")

        note = tk.Label(
            frame,
            text="关闭按钮已禁用；未确认前窗口会保持在最上层。",
            bg="#ffffff",
            fg="#5d6878",
            font=("Microsoft YaHei UI", 9),
            wraplength=390,
            justify="left",
        )
        note.grid(row=4, column=0, columnspan=2, sticky="w", pady=(16, 0))

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)

    def center_window(self) -> None:
        self.root.update_idletasks()
        width = 470
        height = 270
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def keep_on_top(self) -> None:
        self.root.attributes("-topmost", True)
        if should_force_visible(self.is_snoozing):
            self.center_window()
            self.root.deiconify()
            self.root.lift()
        self.root.after(RAISE_INTERVAL_MS, self.keep_on_top)

    def confirm(self) -> None:
        self.state.mark_confirmed(self.local_date, self.task)
        self.root.destroy()

    def snooze(self) -> None:
        self.is_snoozing = True
        if self.snooze_job is not None:
            self.root.after_cancel(self.snooze_job)
        self.snooze_job = self.root.after(SNOOZE_MS, self.show_after_snooze)
        self.root.withdraw()

    def show_after_snooze(self) -> None:
        self.snooze_job = None
        self.is_snoozing = False
        self.root.deiconify()
        self.center_window()
        self.keep_on_top()

    def on_blocked_close(self) -> None:
        messagebox.showinfo("还没确认", f"请先确认今天已经完成：{self.task}。")
        self.keep_on_top()

    def on_unmap(self, _event: tk.Event) -> None:
        if should_restore_on_unmap(self.is_snoozing):
            self.root.after(100, self.restore_from_minimize)

    def restore_from_minimize(self) -> None:
        self.root.deiconify()
        self.center_window()
        self.keep_on_top()


def main() -> int:
    parser = argparse.ArgumentParser(description="每天启动时提醒一项待办")
    parser.add_argument("--task", default="整理书桌", help="当天要完成的事项")
    args = parser.parse_args()
    task = args.task.strip()
    if not task:
        parser.error("任务名称不能为空")
    state = ReminderState()
    if state.confirmed(date.today(), task):
        return 0
    root = tk.Tk()
    ReminderApp(root, task, state)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
