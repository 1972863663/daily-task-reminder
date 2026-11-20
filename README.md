# 每日任务提醒

Windows 桌面提醒工具，使用 Python 3.10+ 自带的 Tkinter。默认事项为“整理书桌”。启动后可以确认完成或稍后提醒，确认状态存储在当前用户的应用数据目录。相同任务当天再次启动时会自动跳过。每次保存最近一次完成的任务。

```powershell
python daily_reminder.py
python daily_reminder.py --task "给盆栽浇水"
```

启动后窗口保持置顶，可选“10 分钟后再提醒”暂时隐藏。适合一次跟踪一项日常任务。
