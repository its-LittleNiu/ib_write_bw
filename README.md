# ib_write_bw

用于并行启动多路 `ib_write_bw` 带宽测试任务，分别包含 Server 端和 Client 端脚本。

## 文件说明

- `ib_write_bw_server.py`：在 Server 端按多个 RDMA Bond 设备并行启动 `ib_write_bw` 服务端任务。
- `ib_write_bw_client.py`：在 Client 端按多个 RDMA Bond 设备和目标 Server IP 并行启动 `ib_write_bw` 客户端任务。

## 运行环境

运行机器需要已安装 `perftest`，并确保 `ib_write_bw` 命令在 `PATH` 中可用。

```bash
ib_write_bw --help
```

## 使用方法

先在 Server 端启动：

```bash
python3 ib_write_bw_server.py
```

再在 Client 端启动：

```bash
python3 ib_write_bw_client.py
```

默认测试时长为 120 秒，默认起始端口为 18515。

指定测试时长：

```bash
python3 ib_write_bw_server.py 300
python3 ib_write_bw_client.py 300
```

指定测试时长和起始端口：

```bash
python3 ib_write_bw_server.py 300 18615
python3 ib_write_bw_client.py 300 18615
```

## 配置说明

Server 端在 `ib_write_bw_server.py` 中修改设备列表：

```python
DEVICES = [
    "mlx5_bond_0",
    "mlx5_bond_1",
    "mlx5_bond_2",
    "mlx5_bond_3",
]
```

Client 端在 `ib_write_bw_client.py` 中修改本机设备和目标 Server IP：

```python
TESTS = [
    ("mlx5_bond_0", "192.168.50.4"),
    ("mlx5_bond_1", "192.168.51.4"),
    ("mlx5_bond_2", "192.168.52.4"),
    ("mlx5_bond_3", "192.168.53.4"),
]
```

Server 和 Client 的设备顺序、测试时长、起始端口需要保持一致。端口按起始端口依次递增，例如起始端口为 `18515` 时：

```text
mlx5_bond_0 -> 18515
mlx5_bond_1 -> 18516
mlx5_bond_2 -> 18517
mlx5_bond_3 -> 18518
```

## 日志

脚本会自动创建日志目录：

- Server 端：`ib_write_bw_server_logs_时间戳/`
- Client 端：`ib_write_bw_client_logs_时间戳/`

每个设备和端口会生成独立日志文件，便于后续排查和统计。
