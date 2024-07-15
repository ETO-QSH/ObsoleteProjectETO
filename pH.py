
import math
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, Eq, solve

ph0 = 0
Kw = 1.0*(10**-14)
Ka1_亚硫酸 = 1.4*(10**-2)
Ka2_亚硫酸 = 6.0*(10**-8)
Ksp_氢氧化铁 = 2.8*(10**-39)

for x in range(1, 125):

    三价铁 = (10**-10)*((1.10)**x)
    氢氧根 = (Ksp_氢氧化铁/三价铁)**(1/3)
    氢离子 = Kw/氢氧根

    亚硫酸根, 亚硫酸氢根, 亚硫酸 = symbols('亚硫酸根 亚硫酸氢根 亚硫酸')

    eq1 = Eq(2*亚硫酸根 + 亚硫酸氢根, 3*三价铁+氢离子-氢氧根)
    eq2 = Eq(亚硫酸根/亚硫酸氢根, Ka2_亚硫酸/氢离子)
    eq3 = Eq(亚硫酸氢根/亚硫酸, Ka1_亚硫酸/氢离子)

    sol = solve((eq1, eq2, eq3), (亚硫酸根, 亚硫酸氢根, 亚硫酸))

    ph1 = -math.log10(氢离子)

    if ph1 > ph0:
        递增 = True
    ph0 = ph1

    print('亚硫酸根/三价铁:', sol[亚硫酸根]/三价铁, '    pH:', -math.log10(氢离子), '    三价铁:', 三价铁, '    pH递增：', 递增)
