#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import time


def build_env() -> dict:
    env = os.environ.copy()

    proxy_url = "http://127.0.0.1:8080"

    env.update({
        "HTTP_PROXY": proxy_url,
        "HTTPS_PROXY": proxy_url,
        "NODE_TLS_REJECT_UNAUTHORIZED": "0",
    })

    return env


def resolve_command(cmd: list[str]) -> list[str]:
    if not cmd:
        raise ValueError("缺少要启动的命令，例如：python wrap_agent.py -- claude")

    executable = cmd[0]
    args = cmd[1:]

    resolved = shutil.which(executable)

    if not resolved:
        raise FileNotFoundError(f"没有找到命令：{executable}")

    return [resolved, *args]


def parse_target_command(argv: list[str]) -> list[str]:
    """
    支持：
      python wrap_agent.py -- claude
      python wrap_agent.py -- python app.py
      python wrap_agent.py claude
    """
    if "--" in argv:
        idx = argv.index("--")
        return argv[idx + 1:]

    return argv


def main() -> int:
    raw_cmd = parse_target_command(sys.argv[1:])

    try:
        target_cmd = resolve_command(raw_cmd)
    except Exception as e:
        print(f"[wrapper] 错误：{e}")
        print()
        print("[wrapper] 用法示例：")
        print("  python wrap_agent.py -- claude")
        print("  python wrap_agent.py -- python app.py")
        print("  python wrap_agent.py -- uv run main.py")
        print("  python wrap_agent.py -- npm run dev")
        return 127

    env = build_env()

    print("=" * 60)
    print("[wrapper] 准备启动 agent 应用")
    print(f"[wrapper] 原始命令：{' '.join(raw_cmd)}")
    print(f"[wrapper] 解析命令：{' '.join(target_cmd)}")
    print("[wrapper] 已注入环境变量：")
    print(f"[wrapper]   HTTP_PROXY={env.get('HTTP_PROXY')}")
    print(f"[wrapper]   HTTPS_PROXY={env.get('HTTPS_PROXY')}")
    print(f"[wrapper]   ALL_PROXY={env.get('ALL_PROXY')}")
    print()
    print("[wrapper] 即将进入目标应用的原生命令行交互")
    print("[wrapper] 退出目标应用后，会回到 wrapper 执行后处理逻辑")
    print("=" * 60)
    print()

    try:
        proc = subprocess.Popen(
            target_cmd,
            env=env,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        return_code = proc.wait()

    except KeyboardInterrupt:
        print()
        print("[wrapper] 收到 Ctrl+C，正在退出。")
        return 130

    print()
    print("=" * 60)
    print("[wrapper] 目标应用已退出")
    print(f"[wrapper] 退出码：{return_code}")
    print("[wrapper] 开始执行后处理逻辑...")
    print("[wrapper] 这里以后可以停止 mitmproxy、解析 .mitm 文件、生成可视化报告")
    print("=" * 60)

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())