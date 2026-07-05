import os
import re
import sys
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="DADS7201 Homework", layout="wide", page_icon="🏠")

BASE_DIR = Path(__file__).resolve().parent


def discover_homeworks():
    """Find sibling HW<N> folders that contain an app.py, sorted by number."""
    hws = []
    for entry in BASE_DIR.iterdir():
        if entry.is_dir() and re.fullmatch(r"HW\d+", entry.name):
            app_file = entry / "app.py"
            if app_file.exists():
                hws.append((entry.name, entry, app_file))
    hws.sort(key=lambda item: int(re.search(r"\d+", item[0]).group()))
    return hws


def run_homework_app(app_file: Path):
    """Execute a homework's app.py in place, isolated from the other tabs."""
    source = app_file.read_text(encoding="utf-8")
    folder = app_file.parent

    original_set_page_config = st.set_page_config
    cwd_before = os.getcwd()
    st.set_page_config = lambda *args, **kwargs: None
    sys.path.insert(0, str(folder))
    os.chdir(folder)
    try:
        exec(
            compile(source, str(app_file), "exec"),
            {"__name__": "__main__", "__file__": str(app_file)},
        )
    except Exception as exc:
        st.error(f"เกิดข้อผิดพลาดขณะโหลด {folder.name}: {exc}")
    finally:
        os.chdir(cwd_before)
        sys.path.remove(str(folder))
        st.set_page_config = original_set_page_config


homeworks = discover_homeworks()

if not homeworks:
    st.warning("ไม่พบโฟลเดอร์ HW ที่มี app.py")
    st.stop()

with st.sidebar:
    st.markdown("### 📚 เลือกงาน")
    selected_name = st.radio(
        "เลือกงาน",
        [name for name, _, _ in homeworks],
        label_visibility="collapsed",
    )
    st.divider()

selected_app_file = next(f for n, _, f in homeworks if n == selected_name)
run_homework_app(selected_app_file)
