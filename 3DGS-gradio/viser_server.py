import viser
import threading
import socket
import pathlib
import open3d as o3d
import numpy as np


viser_servers = {}
viser_server_dict = {}


def _start_viser(port: int, ply_path: pathlib.Path):
    """启动 Viser 并推送模型"""
    if port in viser_servers:
        return
    server = viser.ViserServer(host="127.0.0.1", port=port)
    viser_servers[port] = server
    pcd = o3d.io.read_point_cloud(ply_path)
    pts = np.asarray(pcd.points)
    cols = np.asarray(pcd.colors) if pcd.has_colors() else np.ones_like(pts)
    server.scene.add_point_cloud("/model", pts, cols, point_size=0.02)


def _viser_iframe(port):
    """返回内嵌 iframe 字符串"""
    return f'<iframe src="http://127.0.0.1:{port}" width=100% height=600px frameborder=0></iframe>'


for name, port in [("FreGS", 0), ("COLMAP", 0)]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    ply = pathlib.Path(r"res/point_cloud.ply")
    threading.Thread(target=_start_viser, args=(port, ply), daemon=True).start()
    viser_server_dict[f"{name.lower()}_port"] = port
