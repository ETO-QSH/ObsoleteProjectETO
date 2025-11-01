import gradio as gr
from gradio.themes.builder_app import themes
from viser_server import _viser_iframe, viser_server_dict


process_info = lambda n, i="": n
theme_names = [t().name for t in themes]


with gr.Blocks(title="GPT-SoVITS WebUI") as app:
    gr.Markdown(
        value="本软件以MIT协议开源, 作者不对软件具备任何控制力, 使用软件者、传播软件导出的声音者自负全责."
              + "<br>" + "如不认可该条款, 则不能使用或引用软件包内任何代码和文件. 详见根目录LICENSE."
    )
    gr.Markdown(value="中文教程文档" + "：" + "https://github.com/ETO-QSH")

    with gr.Tabs():
        with gr.TabItem("0-前置数据集获取工具"):
            gr.Markdown(value="0a-UVR5人声伴奏分离&去混响去延迟工具")
            with gr.Row():
                with gr.Column(scale=3):
                    with gr.Row():
                        uvr5_info = gr.Textbox(label=process_info("人声分离WebUI进程输出信息"))
                open_uvr5 = gr.Button(value=process_info("开启人声分离WebUI", "open"), variant="primary", visible=True)
                close_uvr5 = gr.Button(value=process_info("开启人声分离WebUI", "close"), variant="primary", visible=False)

            gr.Markdown(value="0b-语音切分工具")
            with gr.Row():
                with gr.Column(scale=3):
                    with gr.Row():
                        slice_inp_path = gr.Textbox(label="音频自动切分输入路径，可文件可文件夹", value="")
                        slice_opt_root = gr.Textbox(label="切分后的子音频的输出根目录", value="output/slicer_opt")
                    with gr.Row():
                        threshold = gr.Textbox(label="threshold:音量小于这个值视作静音的备选切割点", value="-34")
                        min_length = gr.Textbox(label="min_length:每段最小多长，如果第一段太短一直和后面段连起来直到超过这个值", value="4000")
                        min_interval = gr.Textbox(label="min_interval:最短切割间隔", value="300")
                        hop_size = gr.Textbox(label="hop_size:怎么算音量曲线，越小精度越大计算量越高（不是精度越大效果越好）", value="10")
                        max_sil_kept = gr.Textbox(label="max_sil_kept:切完后静音最多留多长", value="500")
                    with gr.Row():
                        _max = gr.Slider(minimum=0, maximum=1, step=0.05, label="max:归一化后最大值多少", value=0.9, interactive=True)
                        alpha = gr.Slider(minimum=0, maximum=1, step=0.05, label="alpha_mix:混多少比例归一化后音频进来", value=0.25, interactive=True)
                    with gr.Row():
                        n_process = gr.Slider(minimum=1, maximum=4, step=1, label="切割使用的进程数", value=4, interactive=True)
                        slicer_info = gr.Textbox(label=process_info("语音切分进程输出信息"))
                open_slicer_button = gr.Button(value=process_info("开启语音切分", "open"), variant="primary", visible=True)
                close_slicer_button = gr.Button(value=process_info("关闭语音切分", "close"), variant="primary", visible=False)

            gr.Markdown(value="0bb-语音降噪工具")
            with gr.Row():
                with gr.Column(scale=3):
                    with gr.Row():
                        denoise_input_dir = gr.Textbox(label="输入文件夹路径", value="")
                        denoise_output_dir = gr.Textbox(label="输出文件夹路径", value="output/denoise_opt")
                    with gr.Row():
                        denoise_info = gr.Textbox(label=process_info("语音降噪进程输出信息"))
                open_denoise_button = gr.Button(value=process_info("开启语音降噪", "open"), variant="primary", visible=True)
                close_denoise_button = gr.Button(value=process_info("关闭语音降噪", "close"), variant="primary", visible=False)

            gr.Markdown(value="0c-语音识别工具")
            with gr.Row():
                with gr.Column(scale=3):
                    with gr.Row():
                        asr_inp_dir = gr.Textbox(label="输入文件夹路径", value="D:\\GPT-SoVITS\\raw\\xxx", interactive=True)
                        asr_opt_dir = gr.Textbox(label="输出文件夹路径", value="output/asr_opt", interactive=True)
                    with gr.Row():
                        asr_model = gr.Dropdown(
                            label="ASR 模型", choices=["达摩 ASR (中文)", "Faster Whisper (多语种)"],
                            interactive=True, value="达摩 ASR (中文)"
                        )
                        asr_size = gr.Dropdown(label="ASR 模型尺寸", choices=["large"], interactive=True, value="large")
                        asr_lang = gr.Dropdown(label="ASR 语言设置", choices=["zh", "yue"], interactive=True, value="zh")
                        asr_precision = gr.Dropdown(label="数据类型精度", choices=["float32"], interactive=True, value="float32")
                    with gr.Row():
                        asr_info = gr.Textbox(label=process_info("语音识别进程输出信息"))
                open_asr_button = gr.Button(value=process_info("开启语音识别", "open"), variant="primary", visible=True)
                close_asr_button = gr.Button(value=process_info("关闭语音识别", "close"), variant="primary", visible=False)

            gr.Markdown(value="0d-语音文本校对标注工具")
            with gr.Row():
                with gr.Column(scale=3):
                    with gr.Row():
                        path_list = gr.Textbox(label="标注文件路径 (含文件后缀 *.list)", value="xxx.list", interactive=True)
                        label_info = gr.Textbox(label=process_info("音频标注WebUI进程输出信息"))
                open_label = gr.Button(value=process_info("开启音频标注WebUI", "open"), variant="primary", visible=True)
                close_label = gr.Button(value=process_info("关闭音频标注WebUI", "close"), variant="primary", visible=False)

        with gr.TabItem("1-GPT-SoVITS-TTS"):
            with gr.Row():
                with gr.Row():
                    exp_name = gr.Textbox(label="*实验/模型名", value="xxx", interactive=True)
                    gpu_info = gr.Textbox(label="显卡信息", value="0 CPU", visible=True, interactive=False)
                    version_checkbox = gr.Radio(label="版本", value="v2", choices=['v1', 'v2', 'v3'])
                with gr.Row():
                    pretrained_s2G = gr.Textbox(label="预训练SoVITS-G模型路径", value="None", interactive=True, lines=2, max_lines=3, scale=9)
                    pretrained_s2D = gr.Textbox(label="预训练SoVITS-D模型路径", value="None", interactive=True, lines=2, max_lines=3, scale=9)
                    pretrained_s1 = gr.Textbox(label="预训练GPT模型路径", value="None", interactive=True, lines=2, max_lines=3, scale=10)

            with gr.TabItem("1A-训练集格式化工具"):
                gr.Markdown(value="输出logs/实验名目录下应有23456开头的文件和文件夹")
                with gr.Row():
                    with gr.Row():
                        inp_text = gr.Textbox(label="*文本标注文件", value="xxx.list", interactive=True, scale=10)
                    with gr.Row():
                        inp_wav_dir = gr.Textbox(
                            label="*训练集音频文件目录", interactive=True, scale=10,
                            placeholder="填切割后音频所在目录！读取的音频文件完整路径=该目录-拼接-list文件里波形对应的文件名（不是全路径）。如果留空则使用.list文件里的绝对全路径。"
                        )

                gr.Markdown(value="1Aa-文本分词与特征提取")
                with gr.Row():
                    with gr.Row():
                        gpu_numbers1a = gr.Textbox(label="GPU卡号以-分割，每个卡号一个进程", value="0-0", interactive=True)
                    with gr.Row():
                        bert_pretrained_dir = gr.Textbox(
                            label="预训练中文BERT模型路径", interactive=False, lines=2,
                            value="GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large"
                        )
                    with gr.Row():
                        button1a_open = gr.Button(value=process_info("开启文本分词与特征提取", "open"), variant="primary", visible=True)
                        button1a_close = gr.Button(value=process_info("关闭文本分词与特征提取", "close"), variant="primary", visible=False)
                    with gr.Row():
                        info1a = gr.Textbox(label=process_info("文本分词与特征提取进程输出信息"))

                gr.Markdown(value="1Ab-语音自监督特征提取")
                with gr.Row():
                    with gr.Row():
                        gpu_numbers1Ab = gr.Textbox(label="GPU卡号以-分割，每个卡号一个进程", value="0-0", interactive=True)
                    with gr.Row():
                        cnhubert_base_dir = gr.Textbox(
                            label="预训练SSL模型路径", interactive=False, lines=2,
                            value="GPT_SoVITS/pretrained_models/chinese-hubert-base"
                        )
                    with gr.Row():
                        button1b_open = gr.Button(value=process_info("开启语音自监督特征提取", "open"), variant="primary", visible=True)
                        button1b_close = gr.Button(value=process_info("关闭语音自监督特征提取", "close"), variant="primary", visible=False)
                    with gr.Row():
                        info1b = gr.Textbox(label=process_info("语音自监督特征提取进程输出信息"))

                gr.Markdown(value="1Ac-语义Token提取")
                with gr.Row():
                    with gr.Row():
                        gpu_numbers1c = gr.Textbox(label="GPU卡号以-分割，每个卡号一个进程", value="0-0", interactive=True)
                    with gr.Row():
                        pretrained_s2G_ = gr.Textbox(
                            label="预训练SoVITS-G模型路径", interactive=False, lines=2,
                            value="GPT_SoVITS/pretrained_models/s2G488k.pth"
                        )
                    with gr.Row():
                        button1c_open = gr.Button(value=process_info("开启语义Token提取", "open"), variant="primary", visible=True)
                        button1c_close = gr.Button(value=process_info("关闭语义Token提取", "close"), variant="primary", visible=False)
                    with gr.Row():
                        info1c = gr.Textbox(label=process_info("语义Token提取进程输出信息"))

                gr.Markdown(value="1Aabc-训练集格式化一键三连")
                with gr.Row():
                    with gr.Row():
                        button1abc_open = gr.Button(value=process_info("开启训练集格式化一键三连", "open"), variant="primary", visible=True)
                        button1abc_close = gr.Button(value=process_info("关闭训练集格式化一键三连", "close"), variant="primary", visible=False)
                    with gr.Row():
                        info1abc = gr.Textbox(label=process_info("训练集格式化一键三连进程输出信息"))

            with gr.TabItem("1B-微调训练"):
                gr.Markdown(value="1Ba-SoVITS 训练: 模型权重文件在 SoVITS_weights/")
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            batch_size = gr.Slider(minimum=1, maximum=40, step=1, label="每张显卡的batch_size", value=4, interactive=True)
                            total_epoch = gr.Slider(minimum=1, maximum=50, step=1, label="总训练轮数total_epoch", value=8, interactive=True)
                        with gr.Row():
                            text_low_lr_rate = gr.Slider(minimum=0.2, maximum=0.6, step=0.05, label="文本模块学习率权重", value=0.4, visible=False)
                            lora_rank = gr.Radio(label="LoRA秩", value="32", choices=['16', '32', '64', '128'], visible=False)
                            save_every_epoch = gr.Slider(minimum=1, maximum=50, step=1, label="保存频率save_every_epoch", value=4, interactive=True)
                    with gr.Column():
                        with gr.Column():
                            if_save_latest = gr.Checkbox(label="是否仅保存最新的权重文件以节省硬盘空间", value=True, interactive=True, show_label=True)
                            if_save_every_weights = gr.Checkbox(
                                label="是否在每次保存时间点将最终小模型保存至weights文件夹",
                                value=True, interactive=True, show_label=True
                            )
                            if_grad_ckpt = gr.Checkbox(label="v3是否开启梯度检查点节省显存占用", value=False, interactive=False, show_label=True, visible=False)
                        with gr.Row():
                            gpu_numbers_1Ba = gr.Textbox(label="GPU卡号以-分割，每个卡号一个进程", value="0", interactive=True)
                with gr.Row():
                    with gr.Row():
                        button1Ba_open = gr.Button(value=process_info("开启SoVITS训练", "open"), variant="primary", visible=True)
                        button1Ba_close = gr.Button(value=process_info("关闭SoVITS训练", "close"), variant="primary", visible=False)
                    with gr.Row():
                        info1Ba = gr.Textbox(label=process_info("SoVITS训练进程输出信息"))

                gr.Markdown(value="1Bb-GPT 训练: 模型权重文件在 GPT_weights/")
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            batch_size1Bb = gr.Slider(minimum=1, maximum=40, step=1, label="每张显卡的batch_size", value=8, interactive=True)
                            total_epoch1Bb = gr.Slider(minimum=2, maximum=50, step=1, label="总训练轮数total_epoch", value=15, interactive=True)
                        with gr.Row():
                            save_every_epoch1Bb = gr.Slider(minimum=1, maximum=50, step=1, label="保存频率save_every_epoch", value=5, interactive=True)
                            if_dpo = gr.Checkbox(label="是否开启DPO训练选项(实验性)", value=False, interactive=True, show_label=True)
                with gr.Column():
                    with gr.Column():
                        if_save_latest1Bb = gr.Checkbox(label="是否仅保存最新的权重文件以节省硬盘空间", value=True, interactive=True, show_label=True)
                        if_save_every_weights1Bb = gr.Checkbox(
                            label="是否在每次保存时间点将最终小模型保存至weights文件夹",
                            value=True, interactive=True, show_label=True
                        )
                    with gr.Row():
                        gpu_numbers1Bb = gr.Textbox(label="GPU卡号以-分割，每个卡号一个进程", value="0", interactive=True)
                with gr.Row():
                    with gr.Row():
                        button1Bb_open = gr.Button(value=process_info("开启GPT训练", "open"), variant="primary", visible=True)
                        button1Bb_close = gr.Button(value=process_info("关闭GPT训练", "close"), variant="primary", visible=False)
                    with gr.Row():
                        info1Bb = gr.Textbox(label=process_info("GPT训练进程输出信息"))

            with gr.TabItem("1C-推理"):
                gr.Markdown(
                    value="选择训练完存放在SoVITS_weights和GPT_weights下的模型。默认的一个是底模，体验5秒Zero Shot TTS用。"
                )
                with gr.Row():
                    with gr.Row():
                        GPT_dropdown = gr.Dropdown(
                            label="GPT模型列表",
                            choices=["GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"],
                            value="GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt",
                            interactive=True
                        )
                        SoVITS_dropdown = gr.Dropdown(
                            label="SoVITS模型列表",
                            choices=["GPT_SoVITS/pretrained_models/s2G488k.pth"],
                            value="GPT_SoVITS/pretrained_models/s2G488k.pth",
                            interactive=True
                        )
                    with gr.Row():
                        gpu_number_1C = gr.Textbox(label="GPU卡号,只能填1个整数", value="0", interactive=True)
                        refresh_button = gr.Button("刷新模型路径", variant="primary")
                with gr.Row():
                    with gr.Row():
                        batched_infer_enabled = gr.Checkbox(label="启用并行推理版本", value=False, interactive=True,
                                                            show_label=True)
                    with gr.Row():
                        open_tts = gr.Button(value=process_info("开启TTS推理WebUI", "open"), variant='primary', visible=True)
                        close_tts = gr.Button(value=process_info("关闭TTS推理WebUI", "close"), variant='primary', visible=False)
                    with gr.Row():
                        tts_info = gr.Textbox(label=process_info("TTS推理WebUI进程输出信息"))

        with gr.TabItem("2-GPT-SoVITS-变声"):
            gr.Markdown(value="施工中，请静候佳音")
            theme_dropdown = gr.Dropdown(label="可以试试切换主题喵~", choices=theme_names, value="default", interactive=True)
            refresh_html = gr.HTML(elem_id="refresh-box", visible=True, elem_classes="refresh-box")
            theme_dropdown.change(
                fn=lambda theme: f'<meta http-equiv="refresh" content="0; url=?__theme={theme}">',
                inputs=theme_dropdown, outputs=refresh_html
            )

        with gr.TabItem("GPT-SoVITS WebUI"):
            gr.Markdown(
                value="本软件以MIT协议开源, 作者不对软件具备任何控制力, 使用软件者、传播软件导出的声音者自负全责."
                + "<br>" + "如不认可该条款, 则不能使用或引用软件包内任何代码和文件. 详见根目录LICENSE."
            )

            with gr.Column():
                gr.Markdown(value="模型切换")
                with gr.Row():
                    GPT_dropdown_tts = gr.Dropdown(
                        label="GPT模型列表", choices=["GPT模型-A", "GPT模型-B", "GPT模型-C"],
                        value="GPT模型-A", interactive=True
                    )
                    SoVITS_dropdown_tts = gr.Dropdown(
                        label="SoVITS模型列表", choices=["SoVITS模型-A", "SoVITS模型-B", "SoVITS模型-C"],
                        value="SoVITS模型-A", interactive=True
                    )
                    refresh_button_tts = gr.Button("刷新模型路径", variant="primary")

            with gr.Row():
                with gr.Column():
                    gr.Markdown(value="*请上传并填写参考信息")
                    with gr.Row():
                        inp_ref = gr.Audio(label="主参考音频(请上传3~10秒内参考音频，超过会报错！)", type="filepath")
                        inp_refs = gr.File(label="辅参考音频(可选多个，或不选)", file_count="multiple", visible=False)
                    prompt_text = gr.Textbox(label="主参考音频的文本", value="", lines=2)
                    with gr.Row():
                        prompt_language = gr.Dropdown(label="主参考音频的语种", choices=["中文", "英语", "日语"], value="中文")
                        with gr.Column():
                            ref_text_free = gr.Checkbox(
                                label="开启无参考文本模式。不填参考文本亦相当于开启。",
                                value=False, interactive=False, show_label=True
                            )
                            gr.Markdown(
                                "使用无参考文本模式时建议使用微调的GPT" + "<br>" + "听不清参考音频说的啥(不晓得写啥)可以开。开启后无视填写的参考文本。"
                            )

                with gr.Column():
                    gr.Markdown(value="*请填写需要合成的目标文本和语种模式")
                    text = gr.Textbox(label="需要合成的文本", value="", lines=20, max_lines=20)
                    text_language = gr.Dropdown(label="需要合成的文本的语种", choices=["中文", "英语", "日语"], value="中文")

            with gr.Group():
                gr.Markdown(value="推理设置")
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            batch_size_tts = gr.Slider(minimum=1, maximum=200, step=1, label="batch_size", value=20, interactive=True)
                            sample_steps = gr.Radio(label="采样步数(仅对V3生效)", value=32, choices=[4, 8, 16, 32], visible=True)
                        with gr.Row():
                            fragment_interval = gr.Slider(minimum=0.01, maximum=1, step=0.01, label="分段间隔(秒)", value=0.3, interactive=True)
                            speed_factor = gr.Slider(minimum=0.6, maximum=1.65, step=0.05, label="语速", value=1.0, interactive=True)
                        with gr.Row():
                            top_k = gr.Slider(minimum=1, maximum=100, step=1, label="top_k", value=5, interactive=True)
                            top_p = gr.Slider(minimum=0, maximum=1, step=0.05, label="top_p", value=1, interactive=True)
                        with gr.Row():
                            temperature = gr.Slider(minimum=0, maximum=1, step=0.05, label="temperature", value=1, interactive=True)
                            repetition_penalty = gr.Slider(minimum=0, maximum=2, step=0.05, label="重复惩罚", value=1.35, interactive=True)

                    with gr.Column():
                        with gr.Row():
                            how_to_cut = gr.Dropdown(
                                label="怎么切", value="凑四句一切", interactive=True, scale=1,
                                choices=["不切", "凑四句一切", "凑50字一切", "按中文句号。切", "按英文句号.切", "按标点符号切"]
                            )
                            super_sampling = gr.Checkbox(label="音频超采样(仅对V3生效))", value=False, interactive=True, show_label=True)

                        with gr.Row():
                            parallel_infer = gr.Checkbox(label="并行推理", value=True, interactive=True, show_label=True)
                            split_bucket = gr.Checkbox(label="数据分桶(并行推理时会降低一点计算量)", value=True, interactive=True, show_label=True)

                        with gr.Row():
                            seed = gr.Number(label="随机种子", value=-1)
                            keep_random = gr.Checkbox(label="保持随机", value=True, interactive=True, show_label=True)

                        output = gr.Audio(label="输出的语音", sources=[], interactive=False, editable=False)
                        with gr.Row():
                            inference_button = gr.Button("合成语音", variant="primary")
                            stop_infer = gr.Button("终止合成", variant="primary")

            with gr.Group():
                gr.Markdown(value="文本切分工具。太长的文本合成出来效果不一定好，所以太长建议先切。合成会根据文本的换行分开合成再拼起来。")
                with gr.Row():
                    text_inp = gr.Textbox(label="需要合成的切分前文本", value="", lines=4)
                    with gr.Column():
                        _how_to_cut = gr.Dropdown(
                            label="怎么切", value="凑四句一切", interactive=True, scale=1,
                            choices=["不切", "凑四句一切", "凑50字一切", "按中文句号。切", "按英文句号.切", "按标点符号切"]
                        )
                        cut_text = gr.Button("切分", variant="primary")
                    text_opt = gr.Textbox(label="切分后文本", value="", lines=4)
                gr.Markdown(value="后续将支持转音素、手工修改音素、语音合成分步执行。")

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
                            gr.HTML(_viser_iframe(viser_server_dict["fregs_port"]))
                        with gr.TabItem("COLMAP"):
                            gr.HTML(_viser_iframe(viser_server_dict["colmap_port"]))

                with gr.Group():
                    exp = gr.Textbox(label="实验命名", value="xxx", interactive=True, scale=1)
                    model = gr.Dropdown(label="运行算法", choices=["SfM-Free", "LGS A", "FreGS", "COLMAP"], value="FreGS", interactive=True, scale=1)
                    fps = gr.Slider(minimum=0, maximum=15, step=0.5, label="提取帧率", value=3, interactive=True, scale=1)
                    round = gr.Slider(minimum=0, maximum=100000, step=1000, label="训练轮数", value=30000, interactive=True, scale=1)
                    setting = gr.Checkbox(label="打开详细参数配置", value=False, interactive=True, show_label=True, scale=1)

            with gr.Row():
                output_info = gr.Textbox(label="训练日志")

            with gr.Group():
                with gr.Row():
                    run_train = gr.Button("开始训练", variant="primary")
                    stop_train = gr.Button("强行停止", variant="stop")
                    open_viewer = gr.Button("外部浏览", variant="secondary")

    app.launch(server_name="0.0.0.0", inbrowser=True, share=False, server_port=7860, quiet=True)
