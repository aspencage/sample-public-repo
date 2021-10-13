# lda_processing_results

'''
purpose: script for processing the results after the LDA is run in lda_climate_gensim.py
input: LDA model 
output: table with candidate information, predictor variables and wide topic (dependent variable) data 
'''

import pandas as pd 
import numpy as np 
import os 

# gets the dominant LDA topic for each tweet 
# an alternative approach would be - given twitter author screen name - sum partial topic contributions for all pieces
def gen_dominant_topic_table(ldamodel, corpus, 
    texts = None, data_df= None) -> pd.DataFrame:

    # initial output
    dom_top_df = pd.DataFrame()

    # main topic in each doc
    for i, row in enumerate(ldamodel[corpus]): # NOTE - limit num for testing?
        # sorting st dominant topics first 
        row = sorted(row, key=lambda x: (x[1]), reverse = True)
        # get the dominant topic and percent contribution  
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0: # dominant topic 
                # NOTE - likely more efficient to call append only once 
                dom_top_df = dom_top_df.append(pd.Series([int(topic_num), round(prop_topic,4)]), ignore_index=True)                
            else:
                break
        
    dom_top_df.columns = ["Dominant Topic", "Percent Contribution"]

    # option to concatenate to Series of the tweets themselves 
    if texts is not None:
        contents = pd.Series([texts])
        dom_top_df = pd.concat([dom_top_df, contents], axis=1)
        
        return dom_top_df

    # option to concatenate to df of the tweets themselves 
    elif data_df is not None:
        data_df_dom_top = pd.concat([data_df, dom_top_df], axis=1)

        return data_df_dom_top
    
    else:
        return dom_top_df


# generate wide topic by author that can then be merged to the candidate files 
def gen_topic_by_author(data_df_dom_top) -> pd.DataFrame:

    df_topic_by_author = data_df_dom_top[
        ["Tweet ID", "Twitter Author Screen Name", "Dominant Topic", "Percent Contribution"]].groupby(
            ["Twitter Author Screen Name", "Dominant Topic"]).agg({"Percent Contribution" : "mean", "Tweet ID" : "count"})
    df_topic_by_author.rename(columns = {"Tweet ID" : "Tweet Count", 
        "Percent Contribution" : "Percent Contribution when Dominant"}, inplace = True)
    df_topic_by_author.reset_index(inplace=True)
    df_topic_by_author = df_topic_by_author.pivot_table(
        values="Tweet Count", index="Twitter Author Screen Name", columns = "Dominant Topic", fill_value=0)
    df_topic_by_author.reset_index(inplace=True)

    return df_topic_by_author


def normalize_count(df, cols_to_normalize: list, normalizer_col: str) -> pd.DataFrame:
    for col in cols_to_normalize:
        df[col] = df[col] / df[normalizer_col]

    return df 


def bool_count_col(df, cols_to_bool: list) -> pd.DataFrame:
    for col in cols_to_bool:
        df[str(col) + " Bool"] = np.where(df[col] > 0, True, False)

    return df 


def gen_lda_by_author_regression_ready(ldamodel, corpus, 
    data_df, df_predictors) -> pd.DataFrame:

    data_df_dom_top = gen_dominant_topic_table(ldamodel, corpus, data_df=data_df)
    df_topic_by_author = gen_topic_by_author(data_df_dom_top)

    df_topic_by_author["Twitter Author Screen Name"] = df_topic_by_author["Twitter Author Screen Name"].str.lower()
    df_predictors = df_predictors.loc[df_predictors["Climate Bool"] == True]
    df_wide_lda_topics_and_predictors = pd.merge(
        df_predictors,
        df_topic_by_author,
        how="left",
        left_on="Twitter Handle",
        right_on="Twitter Author Screen Name"
        )

    # to run below fn, get list of all columns outside two, might have to do set subtraction and then sort 
    cols_to_normalize = [col for col in df_topic_by_author if isinstance(col, float)]
    normalizer_col = "Total Tweet Count"
    df_wide_lda_topics_and_predictors = normalize_count(
        df_wide_lda_topics_and_predictors,
        cols_to_normalize, normalizer_col
        )

    df_wide_lda_topics_and_predictors = bool_count_col(df_wide_lda_topics_and_predictors, cols_to_normalize)

    return df_wide_lda_topics_and_predictors


if __name__ == "__main__":
    # worked example evaluating appropriateness of including the variables below  

    ### EVALUATE RELATIONSHIPS BETWEEN PREDICTOR VARIABLES ###

    # df with predictor variables of Tweet authors (political candidates) 
    predictors_ff = "https://raw.githubusercontent.com/patrickncage/sample-public-repo/main/climate_tweet_LDA/example_data/Candidate_predictors_limited-gh-ex_21-10-11.csv"
    df_p_sample = pd.read_csv(predictors_ff)
    
    # remove missing data 
    df_p_sample.dropna(inplace=True) 

    # we want to see how correlated these variables are 
    import plotly.express as px 
    pred_cols = ["Incumbent?", "Age", "Followers Count"]

    fig = px.scatter_matrix(df_p_sample[pred_cols])
    fig.show()

    # we realize in the process there are some major outliers in terms of follower count
    # removing extremely high follower count accounts to reduce biasing regression
    df_p_sample = df_p_sample[df_p_sample["Followers Count"] < np.percentile(df_p_sample["Followers Count"], 95)] 

    fig = px.scatter_matrix(df_p_sample[pred_cols])
    fig.show()

    # this looks generally better


    from scipy.stats import pearsonr, spearmanr, normaltest
    print("age and followers correlation") # both continuous: pearson and spearman correlation coefficient 
    print("pearson r", pearsonr(df_p_sample["Age"], df_p_sample["Followers Count"]))
    print("spearman rho", spearmanr(df_p_sample["Age"], df_p_sample["Followers Count"]))
    print()

    # investigating normality of our continuous variables

    # followers count
    px.histogram(df_p_sample["Followers Count"]).show()
    # this is clearly not N, but looks like a candidate for a log(x+1) transformation
    px.histogram(np.log1p(df_p_sample["Followers Count"])).show()
    # this looks better. but is it normal enough for ANOVA?
    print("normality test-pvalue:", normaltest(df_p_sample["Followers Count"]).pvalue)
    # this extreme small p value leads us to reject the null H that the transformed distribution is N
    # typically, we would likely proceed with other statistical tests and transformations
    # here we decide to proceed with visual inspection of the relationship through a boxplot

    # age
    px.histogram(df_p_sample["Age"]).show()
    # does not look normal, is it normal enough for ANOVA?
    print("normality test-pvalue:", normaltest(df_p_sample["Age"]).pvalue)
    # this extremely small p value leads us to reject the null H that the distribution is N
    # we decide to proceed with visual inspection through a boxplot

    print("followers and incumbency relationship")
    x,y = "Incumbent?", "Followers Count"
    fig = px.box(df_p_sample, x=x, y=y).show()
    print()
    '''it seems there's some relationship between follower count and incumbency
    where incumbents generally have a higher follower count
    however for this analysis we deem it not so extreme that we need to exclude on variable
        Incumbent: Yes, interquartile range: 1272 - 6852.5 followers
        Incumbent No: IQR: 307 - 4147 followers
    '''

    print("age and incumbency relationship")
    x,y = "Incumbent?", "Age"
    fig = px.box(df_p_sample, x=x, y=y).show()
    print() 
    '''similarly, it seems there's some relationship between age and incumbency
    where incumbents are generally older
    however for this analysis we deem it not so extreme that we need to exclude on variable
        Incumbent: Yes, IQR: 42 - 65 years old
        Incumbent No: IQR: 35 - 53 yo
    '''
