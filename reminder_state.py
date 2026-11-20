from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Any



APP_DIR_NAME = "DailyTaskReminder"
STATE_FILE_NAME = "state.json"


def default_state_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        base_dir = Path(appdata)
    else:
        base_dir = Path.home() / "AppData" / "Roaming"
    return base_dir / APP_DIR_NAME / STATE_FILE_NAME


class ReminderState:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_state_path()

    def load(self) -> dict[str, Any]:
        try:
            with self.path.open("r", encoding="utf-8") as state_file:
                data = json.load(state_file)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

        if isinstance(data, dict):
            return data
        return {}

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as state_file:
            json.dump(data, state_file, ensure_ascii=False, indent=2)

    def confirmed(self, local_date: date, task: str) -> bool:
        data = self.load()
        return data.get("date") == local_date.isoformat() and data.get("task") == task

    def mark_confirmed(self, local_date: date, task: str) -> None:
        self.save({"date": local_date.isoformat(), "task": task})
