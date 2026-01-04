import os
import sys
import asyncio
import time
import multiprocessing as mp
import uvicorn
from pathlib import Path
import httpx


os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning'

# Ensure project root is on sys.path so absolute imports work when running as a script
_current_dir = Path(__file__).resolve().parent
_project_root = _current_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# ANSI color codes
CYAN = '\033[36m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
RED = '\033[31m'
RESET = '\033[0m'

def _enable_windows_ansi_colors() -> None:
    """
    Enable ANSI escape sequence processing in the Windows 10+ console
    so that color codes like '\033[31m' render correctly.
    """
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        for std_handle in (-11, -12):  # STD_OUTPUT_HANDLE, STD_ERROR_HANDLE
            handle = kernel32.GetStdHandle(std_handle)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    except Exception:
        # Best-effort: if we cannot enable, continue without colors
        pass

def _serve_backend() -> None:
    from core.backend.app import app
    host = os.environ.get("WISEFLOW_BACKEND_HOST", "127.0.0.1")
    port = int(os.environ.get("WISEFLOW_BACKEND_PORT", "8077"))
    try:
        uvicorn.run(app, host=host, port=port, log_level="warning")
    except KeyboardInterrupt:
        pass
    finally:
        # Ensure child process flushes log queues on graceful exit
        try:
            from core.tools.general_utils import shutdown_logger
            shutdown_logger()
        except Exception:
            pass


def _run_tasks() -> None:
    # Import task scheduler routines
    from core.run_task import check_on_startup, schedule_task

    # Always wait for backend readiness (run_task depends on backend)
    host = os.environ.get("WISEFLOW_BACKEND_HOST", "127.0.0.1")
    port = int(os.environ.get("WISEFLOW_BACKEND_PORT", "8077"))
    timeout_total = int(os.environ.get("WISEFLOW_BACKEND_READY_TIMEOUT", "20"))
    deadline = time.perf_counter() + timeout_total
    ready = False
    while time.perf_counter() < deadline:
        try:
            url = f"http://{host}:{port}/list_config"
            with httpx.Client(timeout=3) as client:
                r = client.get(url)
                if r.status_code == 200:
                    ready = True
                    break
        except Exception:
            pass
        time.sleep(0.5)
    if not ready:
        print(f"{RED}[wiseflow] Backend not ready after wait, continuing anyway...{RESET}")

    try:
        asyncio.run(check_on_startup())
        schedule_task()
    except KeyboardInterrupt:
        pass
    finally:
        # Ensure child process flushes log queues on graceful exit
        try:
            from core.tools.general_utils import shutdown_logger
            shutdown_logger()
        except Exception:
            pass

def main() -> None:
    """Unified entrypoint: run API backend and task scheduler together.

    Behavior can be controlled via environment variables:
    - WISEFLOW_DISABLE_TASKS=1 to disable scheduler
    - WISEFLOW_BACKEND_HOST / WISEFLOW_BACKEND_PORT to configure API bind
    """

    disable_tasks = os.environ.get("WISEFLOW_DISABLE_TASKS", "0") == "1"

    # Ensure a safe start method across platforms (Windows requires spawn)
    try:
        if os.name == "nt" or sys.platform == "darwin":
            mp.set_start_method("spawn", force=True)
    except Exception:
        pass

    processes = []

    # Mark child processes to prevent re-initialization
    os.environ["WISEFLOW_CHILD_PROCESS"] = "1"

    # Always start backend (run_task depends on backend)
    p_api = mp.Process(target=_serve_backend, name="wiseflow-backend")
    p_api.start()
    processes.append(p_api)

    if not disable_tasks:
        p_tasks = mp.Process(target=_run_tasks, name="wiseflow-tasks")
        p_tasks.start()
        processes.append(p_tasks)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        pass
    finally:
        from core.tools.general_utils import shutdown_logger
        shutdown_logger()  # 确保日志队列刷新
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join()
            p.close()


if __name__ == "__main__":
    # Print banner only in main process, before spawning children
    if os.environ.get("WISEFLOW_CHILD_PROCESS") != "1":
        _enable_windows_ansi_colors()
        print(f"\n{CYAN}{'#' * 50}{RESET}")
        print(f"{GREEN}Wiseflow v4.30{RESET}")
        print(f"{YELLOW}⚠️  重要提示：本工具仅限于获取公开发布的非知识产权内容{RESET}")
        print(f"{BLUE}适用范围：企业门户、政府部门、行业协会等的公告栏、通知栏、新闻发布栏等{RESET}")
        print(f"{RED}严格禁止：用于媒体网站、交易网站等受知识产权保护内容的获取{RESET}")
        print(f"{MAGENTA}免责声明：使用结果由用户自行承担，请谨慎评估后使用{RESET}")
        print(f"{GREEN}wiseflow pro 版本：更全面的获取能力、更佳的提取效果、免部署一键运行 + web UI 界面，详情了解：https://shouxiqingbaoguan.com/{RESET}")
        print(f"{CYAN}{'#' * 50}{RESET}\n")
    
    main()
