import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ------------------------------------------------------------
# Configuration

def __format_significant_digits(x: float, digits: int):
    return np.format_float_positional(x, digits, fractional=False).rstrip('.')

plt.style.use('ggplot')

pd.options.display.latex.repr = True

pd.options.display.max_colwidth = 80
pd.options.display.max_rows = None

pd.options.display.precision = 2
pd.options.display.float_format = (lambda x: __format_significant_digits(x, pd.options.display.precision))
