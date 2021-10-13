# lda_regression

import os 
import pandas as pd
import numpy as np  
import statsmodels.formula.api as smf
import time 


# create a patsy formula that can deal with categorical variables to reduce manual use 
def gen_patsy_formula(df: pd.DataFrame, resp_col: str, expl_var_cols: list) -> str:

    patsy_formula = f"Q('{resp_col}') ~ "
    for col_name in expl_var_cols:
        form_addn = f"Q('{col_name}')"
        if df[col_name].dtype == "object":
            form_addn = f"C({form_addn})"
        patsy_formula += form_addn + " + "
    return patsy_formula[:-3] # to deal with hanging ' + '


def gen_factor_response_dict(factor_data: list, bonferri_cxn: bool = False,
    response_vars: list = None) -> dict:

    factor_response_dict = {}
    alpha_vals = [0.001, 0.01, 0.05, 0.1]
    if bonferri_cxn == True:
        alpha_vals = [a / len(response_vars) * len(factor_data) for a in alpha_vals] 

    for iv in factor_data:
        if abs(iv[1]) > 0.001:
            factor_response_dict[iv[0]] = f"{round(iv[1],4)} ({round(iv[2],4)})"
        else:
            sn_coeff = f"{iv[1]:.3E}"
            sn_ste = f"{iv[2]:.3E}"
            factor_response_dict[iv[0]] = f"{sn_coeff} ({sn_ste})"
        
        sig_star = None
        if iv[3] <= alpha_vals[0]:
            sig_star = "***"
        elif iv[3] <= alpha_vals[1]:
            sig_star = "**"
        elif iv[3] <= alpha_vals[2]:
            sig_star = "*"
        elif iv[3] <= alpha_vals[3]:
            sig_star = "+"
        
        if sig_star is not None:   
            factor_response_dict[iv[0]] += f" {sig_star}"

    return factor_response_dict


def logit_table_multi_response_var(df: pd.DataFrame, response_vars: list, 
    expl_var_cols: list, bonferri_cxn: bool = True, print_ = False) -> pd.DataFrame:

    model_dict_list = []

    for y_var in response_vars:
        patsy_formula = gen_patsy_formula(df, y_var, expl_var_cols)
        
        expl_int = ["Intercept"] + expl_var_cols

        log_reg = smf.logit(patsy_formula, df).fit()
        if print_ == True:
            print(log_reg.summary())
            print("\n\n")

        y_name = f"LDA Topic: {str(y_var[:-5])}" # get rid of Bool at end 
        pr2 = log_reg.prsquared
        aic = log_reg.aic
        coeffs = log_reg.params
        std_err = log_reg.bse
        pvalues = log_reg.pvalues # pd.Series  

        factor_data = list(zip(expl_int, coeffs, std_err, pvalues))
        # list where each tuple is (col_name, coeff, std_err, pvalue)

        factor_response_dict = gen_factor_response_dict(factor_data, 
            bonferri_cxn=bonferri_cxn, response_vars = response_vars)

        model_dict = {
            "Response Variable" : y_name,
            "McFadden's pseudo-R-squared" : pr2,
            "AIC" : aic
            }

        model_dict = dict(**model_dict, **factor_response_dict)

        model_dict_list.append(model_dict)

    df = pd.DataFrame(model_dict_list)

    return df 



if __name__ == "__main__":
        
    fp = r"C:\Users\patri\Dropbox\TFGHGMI Internal\UCSC CSP - grad school\Capstone Research\Research Twitter Data HD"
    fn = "Merged_12Apr21_0740_Candidate_27Feb21_2026_lda-topic-counts_sample_09Oct21_1545_norm-bool"
    os.chdir(fp)
    df = pd.read_csv(fn+".csv")

    expl_var_cols = ["Incumbent?", "Chamber", "abs(PVI Margin)", "Gender", "Age", 
        "Asthma rate", "Clean energy jobs normalized"]

    # can feed upper number from LDA_model 
    resp_var_cols = [(str(int(n)) + " Bool") for n in np.arange(0,34,1)]

    # converts bools to 1 and 0, which statsmodels requires instead 
    for col in resp_var_cols:
        df[col] = np.where(df[col] == True, 1, 0)

    df_logit_models = logit_table_multi_response_var(df, resp_var_cols, 
        expl_var_cols, bonferri_cxn = True, print_=False) 