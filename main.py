import os
import re
import subprocess
import sys
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="DADS7201 Homework", layout="wide", page_icon="🏠")

BASE_DIR = Path(__file__).resolve().parent


def ensure_submodules():
    """Some hosts (e.g. Streamlit Community Cloud) don't clone submodules,
    leaving HW folders that are submodules empty. Init/update them here."""
    if not (BASE_DIR / ".gitmodules").exists():
        return
    try:
        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            cwd=BASE_DIR,
            check=True,
            capture_output=True,
            timeout=120,
        )
    except Exception as exc:
        st.warning(f"ไม่สามารถโหลด git submodule อัตโนมัติได้: {exc}")


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


ensure_submodules()
homeworks = discover_homeworks()

if not homeworks:
    st.warning("ไม่พบโฟลเดอร์ HW ที่มี app.py")
    st.stop()

with st.sidebar:
    st.markdown("### 📚 เลือกงาน")
    # Default to the highest-numbered HW folder (i.e. the most recently
    # added homework) rather than always starting on HW1.
    selected_name = st.radio(
        "เลือกงาน",
        [name for name, _, _ in homeworks],
        index=len(homeworks) - 1,
        label_visibility="collapsed",
    )
    st.divider()

st.markdown(
    """
    <style>
    .sidebar-credit {
        position: fixed;
        bottom: 14px;
        left: 16px;
        font-size: 0.72rem;
        line-height: 1.5;
        color: #94a3b8;
        z-index: 999;
    }
    </style>
    <div class="sidebar-credit">Pimkanit Thongsrikaew<br>6810422011</div>
    """,
    unsafe_allow_html=True,
)

selected_app_file = next(f for n, _, f in homeworks if n == selected_name)
run_homework_app(selected_app_file)
