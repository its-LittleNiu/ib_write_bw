#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
并行启动多个 ib_write_bw server 端任务。

默认测试 4 个 RDMA Bond 设备：
mlx5_bond_0 ~ mlx5_bond_3

使用方法：
1. 默认测试 120 秒，端口从 18515 开始：
   python3 ib_write_bw_server.py

2. 测试 300 秒，端口从 18515 开始：
   python3 ib_write_bw_server.py 300

3. 测试 300 秒，端口从 18615 开始：
   python3 ib_write_bw_server.py 300 18615

端口分配示例：
base_port = 18515 时：
mlx5_bond_0 -> 18515
mlx5_bond_1 -> 18516
mlx5_bond_2 -> 18517
mlx5_bond_3 -> 18518
"""

import os
import sys
import time
import subprocess
from datetime import datetime


# ===== 可按实际情况修改的固定参数 =====

# 要并行测试的 RDMA Bond 设备
DEVICES = [
    "mlx5_bond_0",
    "mlx5_bond_1",
    "mlx5_bond_2",
    "mlx5_bond_3",
]

# ib_write_bw 的固定参数
IB_PORT = "1"
MESSAGE_SIZE = "4096"
QUEUE_DEPTH = "8"

# 默认持续时间。也可以在命令行第一个参数中覆盖。
DEFAULT_DURATION = 120

# 默认起始端口。也可以在命令行第二个参数中覆盖。
DEFAULT_BASE_PORT = 18515


def get_duration_and_base_port():
    """
    读取命令行参数。

    例子：
    python3 ib_write_bw_server.py
    python3 ib_write_bw_server.py 300
    python3 ib_write_bw_server.py 300 18615
    """
    duration = DEFAULT_DURATION
    base_port = DEFAULT_BASE_PORT

    if len(sys.argv) >= 2:
        duration = int(sys.argv[1])

    if len(sys.argv) >= 3:
        base_port = int(sys.argv[2])

    return duration, base_port


def make_log_dir():
    """
    创建本次测试的日志目录。
    """
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "ib_write_bw_server_logs_" + now
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def main():
    duration, base_port = get_duration_and_base_port()
    log_dir = make_log_dir()

    print("=" * 70)
    print("ib_write_bw Server 端并行测试开始")
    print("持续时间:", duration, "秒")
    print("起始端口:", base_port)
    print("日志目录:", log_dir)
    print("=" * 70)

    process_list = []

    # 逐个启动进程。Popen 不会等待命令结束。
    # 所以 4 个进程会并行运行。
    for index in range(len(DEVICES)):
        device = DEVICES[index]
        port = base_port + index

        command = [
            "ib_write_bw",
            "-d", device,
            "-i", IB_PORT,
            "-m", MESSAGE_SIZE,
            "-q", QUEUE_DEPTH,
            "--report_gbits",
            "-F",
            "-p", str(port),
            "-D", str(duration),
        ]

        log_file_name = device + "_port_" + str(port) + ".log"
        log_file_path = os.path.join(log_dir, log_file_name)

        # 将标准输出和报错输出都保存到同一个日志文件。
        log_file = open(log_file_path, "w", encoding="utf-8")

        # 先将本次实际执行的命令写入日志，便于后续排查。
        log_file.write("开始时间: " + datetime.now().strftime("%F %T") + "\n")
        log_file.write("执行命令:\n")
        log_file.write(" ".join(command) + "\n")
        log_file.write("=" * 70 + "\n")
        log_file.flush()

        print("启动:", " ".join(command))

        try:
            process = subprocess.Popen(
                command,
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )

            # 保存 process 和 log_file。
            # 测试结束前不能关闭 log_file。
            process_list.append({
                "device": device,
                "port": port,
                "process": process,
                "log_file": log_file,
                "log_file_path": log_file_path,
            })

        except FileNotFoundError:
            print("错误：未找到 ib_write_bw，请确认 perftest 已安装且命令在 PATH 中。")
            log_file.close()
            sys.exit(1)

    print()
    print("全部 Server 端进程已启动。现在可在 Client 端执行对应脚本。")
    print()

    # 等待所有并行测试结束。
    for item in process_list:
        return_code = item["process"].wait()

        item["log_file"].write("\n" + "=" * 70 + "\n")
        item["log_file"].write("结束时间: " + datetime.now().strftime("%F %T") + "\n")
        item["log_file"].write("退出码: " + str(return_code) + "\n")
        item["log_file"].close()

        print(
            "结束:",
            item["device"],
            "端口:", item["port"],
            "退出码:", return_code,
        )
        print("日志:", item["log_file_path"])

    print()
    print("全部 Server 端测试完成。")


if __name__ == "__main__":
    main()
