from utils.utils_5342 import get_type, _json_schema_to_python_type
from gradio_client import utils

utils.get_type = get_type
utils._json_schema_to_python_type = _json_schema_to_python_type

import json
import tool
import queue
import subprocess
import gradio as gr
from gradio.themes.builder_app import themes
from tool import LOG_QUEUE, _start_train, _stop_train

css = """
.json-view {
    font-size: 12px !important;
}
"""

with gr.Blocks(title="3DGS-show WebUI", css=css) as app:
    gr.Markdown(
        value="本软件以MIT协议开源, 作者不对软件具备任何控制力, 使用软件者、传播软件导出的声音者自负全责."
              + "<br>" + "如不认可该条款, 则不能使用或引用软件包内任何代码和文件. 详见根目录LICENSE."
    )
    gr.Markdown(value="中文教程文档" + "：" + "https://github.com/ETO-QSH")

    with gr.Tabs():
        with gr.TabItem("3DGS-show"):
            gr.Markdown(value="不知道写什么反正放点东西占个位置，Ciallo～ (∠・ω< )⌒★")

            with gr.Row():
                video_input = gr.Video(label="上传视频（拖拽或点击）", sources=["upload", "webcam"], scale=1)
                loading_3d = r"res/thermal-ex_from_arknights.glb"

                with gr.Column(scale=2):
                    with gr.Tabs():
                        with gr.TabItem("3DGS"):
                            model3d_3dgs = gr.Model3D(label="3DGS 模型", interactive=False)
                        with gr.TabItem("SfM-Free"):
                            model3d_sfmfree = gr.Model3D(label="SfM-Free 模型", interactive=False)
                        with gr.TabItem("LGS A"):
                            model3d_lgsa = gr.Model3D(label="LGS A 模型", interactive=False)
                        with gr.TabItem("FreGS"):
                            model3d_fregs = gr.Model3D(label="FreGS 模型", interactive=False)
                        with gr.TabItem("DivShot"):
                            model3d_divshot = gr.Model3D(label="DivShot 模型", interactive=False)

                models = {
                    "3DGS": model3d_3dgs, "SfM-Free": model3d_sfmfree, "LGS A": model3d_lgsa,
                    "FreGS": model3d_fregs, "DivShot": model3d_divshot
                }

                with gr.Group():
                    exp = gr.Textbox(label="实验命名", value="xxx", interactive=True, scale=1)
                    model = gr.Dropdown(label="运行算法", choices=list(models.keys()), value="3DGS", interactive=True)
                    fps = gr.Slider(minimum=0, maximum=15, step=0.5, label="提取帧率", value=3, interactive=True)
                    round = gr.Slider(minimum=0, maximum=100000, step=1000, label="训练轮数", value=30000, interactive=True)
                    setting = gr.Checkbox(label="采用详细参数配置", interactive=False, value=False, show_label=True)

            with gr.Row():
                output_info = gr.Textbox(label="训练日志", interactive=False, value="", elem_id="logbox", max_lines=32)

            with gr.Group():
                with gr.Row():
                    run_train = gr.Button("开始训练", variant="primary")
                    stop_train = gr.Button("强行停止", variant="stop", interactive=False)
                    open_viewer = gr.Button("外部浏览", variant="secondary")

            def poll_queue():
                try:
                    line = LOG_QUEUE.get_nowait()
                    if line.strip() == "CLEAR_TOKEN":
                        output_info.value = ""
                        return ""
                    output_info.value += line
                    gr.HTML(f"""
                        <script>
                            var box = document.getElementById('logbox');
                            if(box) box.scrollTop = box.scrollHeight;
                        </script>
                    """, visible=False)
                except queue.Empty:
                    pass
                return output_info.value

            app.load(poll_queue, outputs=output_info, every=0.5)

            def start_train_ui(video, fps, round, exp):
                if video is None:
                    gr.Warning("请先上传视频")
                    return [gr.update(), gr.update(), gr.update()]
                _start_train(video, fps, round, exp)
                return [gr.update(interactive=False), gr.update(interactive=True), gr.update(value=loading_3d, visible=True)]

            run_train.click(
                fn=start_train_ui,
                inputs=[video_input, fps, round, exp],
                outputs=[run_train, stop_train, models[model.value]]
            )

            def update_ui_after_train():
                if tool.FINAL_MODEL_PATH:
                    return [gr.update(interactive=True), gr.update(interactive=False), gr.update(value=tool.FINAL_MODEL_PATH)]
                return [gr.update(), gr.update(), gr.update()]

            output_info.change(
                fn=update_ui_after_train,
                outputs=[run_train, stop_train, models[model.value]]
            )

            def open_divshot():
                try:
                    subprocess.run(["divshot.exe", "-i", tool.MODEL_PATHS[model.value]])
                except KeyError:
                    gr.Warning("模型未生成")

            open_viewer.click(fn=open_divshot)

            def stop_train_ui():
                if _stop_train():
                    return [gr.update(interactive=True), gr.update(interactive=False), gr.update(value="empty.obj")]
                else:
                    return [gr.update(), gr.update(), gr.update()]

            stop_train.click(
                fn=stop_train_ui,
                outputs=[run_train, stop_train, models[model.value]]
            )

        with gr.TabItem("主题切换测试"):
            gr.Markdown(value="施工中，请静候佳音")
            theme_dropdown = gr.Dropdown(label="可以试试切换主题喵~", choices=[t().name for t in themes], value="default", interactive=True)
            refresh_html = gr.HTML(elem_id="refresh-box", visible=True, elem_classes="refresh-box")
            theme_dropdown.change(
                fn=lambda theme: f'<meta http-equiv="refresh" content="0; url=?__theme={theme}">',
                inputs=theme_dropdown, outputs=refresh_html
            )

            def parse_json(code_str):
                try:
                    return json.loads(code_str)[model.value]
                except Exception as e:
                    return {"JsonError": e}

            with gr.Group():
                with gr.Row():
                    with open("config.json", "r", encoding="utf-8") as cfg:
                        code = gr.Code(value=cfg.read(), language="json", label="JSON 编辑器")
                    out = gr.Json(label="解析结果", elem_classes="json-view")

                btn = gr.Button("解析", variant="primary")
                btn.click(parse_json, inputs=code, outputs=out)

    app.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True, share=False, quiet=True)
