from manim import *


class FormulaTransform(Scene):
    def construct(self):
        # 创建原始公式
        formula1 = MathTex("\\lim_{x \\to 0} \\frac{x^3}{x-sin(x)}")

        # 创建变形后的公式
        formula2 = MathTex("\\lim_{x \\to 0} \\frac{x^3}{x-sin(x)} = \\lim_{x \\to 0} \\frac{3x^2}{1-cos(x)}")
        formula3 = MathTex("\\lim_{x \\to 0} \\frac{x^3}{x-sin(x)} = \\lim_{x \\to 0} \\frac{3x^2}{1-cos(x)} = \\lim_{x \\to 0} \\frac{6x}{sin(x)}")
        formula4 = MathTex("\\lim_{x \\to 0} \\frac{x^3}{x-sin(x)} = \\lim_{x \\to 0} \\frac{3x^2}{1-cos(x)} = \\lim_{x \\to 0} \\frac{6x}{sin(x)} = \\frac{6}{1} = 6")

        # 将原始公式添加到场景中
        self.play(Write(formula1))
        self.wait(1)

        # 变形动画
        self.play(Transform(formula1, formula2))
        self.wait(1)

        self.play(Transform(formula1, formula3))
        self.wait(1)

        self.play(Transform(formula1, formula4))
        self.wait(1)