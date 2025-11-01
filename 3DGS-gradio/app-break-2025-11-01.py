import json
import gradio as gr
from gradio.themes.builder_app import themes
from viser_server import _viser_iframe, viser_server_dict


process_info = lambda n, i="": n
theme_names = [t().name for t in themes]


with gr.Blocks(title="3DGS-show WebUI") as app:
    gr.Markdown(
        value="本软件以MIT协议开源, 作者不对软件具备任何控制力, 使用软件者、传播软件导出的声音者自负全责."
              + "<br>" + "如不认可该条款, 则不能使用或引用软件包内任何代码和文件. 详见根目录LICENSE."
    )
    gr.Markdown(value="中文教程文档" + "：" + "https://github.com/ETO-QSH")

    with gr.Tabs():
        with gr.TabItem("3DGS-show"):
            gr.Markdown(value="不知道写什么反正放点东西占个位置，Ciallo～ (∠・ω< )⌒★")

            with gr.Row():
                video_input = gr.Video(label="上传视频（拖拽或点击）", sources=["upload", "webcam"], format="mp4", scale=1)

                with gr.Column(scale=2):
                    with gr.Tabs():
                        with gr.TabItem("SfM-Free"):
                            gr.Model3D(value=r"res/bee.glb")
                        with gr.TabItem("LGS A"):
                            gr.Model3D(value=r"res/bee.glb")
                        with gr.TabItem("FreGS"):
                            gr.Model3D(value=r"res/bee.glb")
                            # gr.HTML(_viser_iframe(viser_server_dict["fregs_port"]))
                        with gr.TabItem("COLMAP"):
                            gr.Model3D(value=r"res/bee.glb")
                            # gr.HTML(_viser_iframe(viser_server_dict["colmap_port"]))

                with gr.Group():
                    exp = gr.Textbox(label="实验命名", value="xxx", interactive=True, scale=1)
                    model = gr.Dropdown(label="运行算法", choices=["SfM-Free", "LGS A", "FreGS", "COLMAP"], value="FreGS", interactive=True, scale=1)
                    fps = gr.Slider(minimum=0, maximum=15, step=0.5, label="提取帧率", value=3, interactive=True, scale=1)
                    round = gr.Slider(minimum=0, maximum=100000, step=1000, label="训练轮数", value=30000, interactive=True, scale=1)
                    setting = gr.Checkbox(label="采用详细参数配置", value=False, interactive=False, show_label=True, scale=1)

            with gr.Row():
                output_info = gr.Textbox(label="训练日志")

            with gr.Group():
                with gr.Row():
                    run_train = gr.Button("开始训练", variant="primary")
                    stop_train = gr.Button("强行停止", variant="stop")
                    open_viewer = gr.Button("外部浏览", variant="secondary")

        with gr.TabItem("主题切换测试"):
            gr.Markdown(value="施工中，请静候佳音")
            theme_dropdown = gr.Dropdown(label="可以试试切换主题喵~", choices=theme_names, value="default", interactive=True)
            refresh_html = gr.HTML(elem_id="refresh-box", visible=True, elem_classes="refresh-box")
            theme_dropdown.change(
                fn=lambda theme: f'<meta http-equiv="refresh" content="0; url=?__theme={theme}">',
                inputs=theme_dropdown, outputs=refresh_html
            )

            def parse_json(code_str):
                try:
                    return json.loads(code_str)
                except Exception as e:
                    return {"JsonError": e}

            with gr.Group():
                with gr.Row():
                    with open("config.json", "r", encoding="utf-8") as cfg:
                        code = gr.Code(value=cfg.read(), language="json", label="JSON 编辑器")
                    out = gr.Json(label="解析结果")

                btn = gr.Button("解析", variant="primary")
                btn.click(parse_json, inputs=code, outputs=out)

    app.launch(server_name="0.0.0.0", inbrowser=True, share=False, server_port=7860, quiet=True)
