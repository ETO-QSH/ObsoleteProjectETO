def create_vertical_svg(lines, output_file="poem.svg", font_size=32, col_spacing=40, line_height_ratio=1.125, width=900, height=1400):
    """
    将中文诗句生成竖排 SVG（从右到左，每行变一列，从上到下书写）

    :param lines: 字符串列表，每项是一行诗（按从上到下顺序）
    :param output_file: 输出的 SVG 文件名
    :param font_size: 字体大小
    :param col_spacing: 列之间的水平间距（控制紧凑度）
    :param line_height_ratio: 行高比例（控制垂直紧凑度，越小越紧凑）
    :param width: SVG 画布宽度
    :param height: SVG 画布高度
    """
    line_height = int(font_size * line_height_ratio)

    # 开始构建 SVG 内容
    svg_lines = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        '<style>',
        '  @font-face {',
        '    font-family: "STXingkai";',
        '    src: local("华文行楷"), local("STXingkai"), local("STXinwei"), serif;',
        '  }',
        '  .char {',
        '    font-family: "STXingkai", "华文行楷", "KaiTi", serif;',
        '    font-size: ' + str(font_size) + 'px;',
        '    text-anchor: middle;',
        '    dominant-baseline: middle;',
        '    fill: #1a1a1a;',
        '  }',
        '</style>',
        '<g transform="translate(' + str(width - 50) + ', ' + str(font_size * 2) + ')">'
    ]

    # 从右到左排列列（最后一行在最右边，第一行在最左边 → 反向遍历）
    for i, text in enumerate(reversed(lines)):
        x_offset = -i * col_spacing
        group = [f'  <g transform="translate({x_offset}, 0)">']
        for j, char in enumerate(text.strip()):
            y = (j + 1) * line_height
            group.append(f'    <text x="0" y="{y}" class="char">{char}</text>')
        group.append('  </g>')
        svg_lines.extend(group)

    svg_lines.append('</g>')
    svg_lines.append('</svg>')

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg_lines))

    print(f"✅ SVG 文件已生成：{output_file}")
    print(f"   共 {len(lines)} 行，生成 {len(lines)} 列（从右到左）")


# ======================
# ✅ 使用示例
# ======================

if __name__ == "__main__":
    # 按你原文的顺序传入每一行
    poem_lines = [
        "你好似无法捉摸的风",
        "闭上眼又似日暮余霞",
        "你的脑海里究竟在想什么呢",
        "你睁开的双眼",
        "眸子仿若琉璃",
        "似乎带着淡淡晴空的气息",
        "苍穹为你晴空万里",
        "催繁花盛开",
        "绽放是因你晴朗似骄阳"
    ]

    # 生成 SVG
    create_vertical_svg(
        lines=poem_lines[::-1],
        output_file="test.svg",
        font_size=32,
        col_spacing=40,        # 越小越紧凑
        line_height_ratio=1.1  # 越小越紧凑（建议 1.0 ~ 1.2）
    )
