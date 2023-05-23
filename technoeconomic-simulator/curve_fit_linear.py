# curve_fit_linear 

# purpose: simply find best linear fn between data points 
## feed arrays into the function (so things like the watts issue resolved externally)

## output: return dictionary in the format of the JSON obj  

from numpy.core.fromnumeric import std
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import os 
from scipy import optimize
from scipy import stats

def line(x, m, b):
    return m*x + b


def get_linear_fn(x: np.ndarray, y: np.ndarray,
    y_name: str, y_units: str,
    plot: bool = True, title: str = None,
    ):
    
    x = np.array(x) 
    y = np.array(y) 

    popt_line, pcov_line = optimize.curve_fit(
        f = line,
        xdata = x, 
        ydata = y
        )

    y_line = line(x, popt_line[0], popt_line[1])
    equa = "y = m*x + b"
    m = popt_line[0]
    b = popt_line[1]
    if popt_line[1] >= 0:
        param_equa = f"y = {round(m,2)}x + {round(b,2)}"
    elif popt_line[1] <0:
        param_equa = f"y = {round(m,2)}x - {abs(round(b,2))}"

    # float here and elsewhere bc numpy int64 is not JSON serializable 
    r2 = float(stats.pearsonr(x, y)[0]**2)

    if plot:
        fig, ax = plt.subplots()
        _ = ax.scatter(x, y, label="data")
        _ = ax.plot(x, y_line, label="line predicted")
        if title is not None:
            _ = ax.set_title(title)
        _ = ax.legend()
        plt.show()

    fn_dict = {
        "response variable": y_name,
        "response unit": y_units,
        "type": "linear",
        "parameterized equation": param_equa,
        "equation": equa,
        "parameters": {
            "m": float(m),
            "b": float(b)
            },
        "domain": (float(min(x)), float(max(x))),
        "range": (float(min(y)), float(max(y))),
        "r2": r2
        }

    return fn_dict

if __name__ == "__main__":
    # STEP 1 data gathered and imported 
    fp = r"PATH/TO/DIRECTORY"
    fn = "PART-OBJECT-IN-STRUCTURED-TEMPLATE"
    os.chdir(fp)
    df = pd.read_excel(fn + ".xlsx")

    # define variables 
    watts = pd.to_numeric(df["Watts"].str[:-2])
    flow = df["Flow Rate, (gpm)"]
    cost = df["Price"]

    x = flow
    y = watts

    y_name = "electricity"
    y_units = "watts"
    title = "Data and fit: Unit watts by flow rate"

    fn_dict = get_linear_fn(x, y, y_name, y_units, title = title, plot = True)
    print(fn_dict)

    y, y_name, y_units = cost, "cost", "USD"
    title = "Data and fit: Unit cost by flow rate"

    fn_dict = get_linear_fn(x, y, y_name, y_units, title = title, plot = True)
    print(fn_dict)
