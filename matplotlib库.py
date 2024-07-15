
#%matplotlib inline
import numpy as np
import matplotlib.pyplot as plt
x = np.linspace(-10, 10, 40)
y = x**abs(x)
plt.plot(x, y, marker = 'o')
plt.show()
