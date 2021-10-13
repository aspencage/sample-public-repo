# lda_set_and_run

#### script for tuning parameters and running climate change Tweet LDAs ####

from copy import deepcopy 

from lda_climate_gensim import *
from lda_cli_stopwords import custom_stop # iteratively-derived generic and domain specific (climate) stopwords
import lda_processing_results
from lda_regression import *

# filepath and filename for JSON containing climate keywords (iteratively tested over corpus previously)
cli_kw_ff = "https://raw.githubusercontent.com/patrickncage/sample-public-repo/main/climate_tweet_LDA/example_data/climate_tkc_grounded_25May2021_capstone%20research.json"

# NOTE GitHub viewers: load_20_random_appended and load_5_perc_sample have data provided
# simple object for providing a default file(path) when selecting an lda_setting
default_ff = {
    "load_5_perc_sample" : r"https://raw.githubusercontent.com/patrickncage/sample-public-repo/main/climate_tweet_LDA/example_data/lda_5percent_Dem-sample_2020_climate-cleaned.csv",
    "load_20_random_appended" : r"https://raw.githubusercontent.com/patrickncage/sample-public-repo/main/climate_tweet_LDA/example_data/lda_20randcand_sample_2020_climate-cleaned.csv",
    "load_dir" : r"C:\Users\patri\Dropbox\TFGHGMI Internal\UCSC CSP - grad school\Capstone Research\LDA sample data",
    "load_csv" : r"C:\Users\patri\Dropbox\TFGHGMI Internal\UCSC CSP - grad school\Capstone Research\LDA sample data\3 Dem climate tweet corpus\dem_2020_climate_corpus_04Jun21_0954",
    "process_5_percent_sample" : r"E:\Twitter Data",
    "process_corpus_new" : r"E:\Twitter Data"
    }


if __name__ == "__main__": 

    ### GENERATE / IMPORT DATAFRAME AND PROCESS DATA ###

    # in case of repeated code runs in iPython/Jupyter kernel
    try: 
        del df
    except:
        pass

    df_setting = "load_5_perc_sample"
    stopwords_changed = True # for "load_csv" if stopwords have changed since originally compiled
    
    data_full_filepath = default_ff[df_setting]
    df_setting_print = deepcopy(df_setting)
    if df_setting == "load_5_perc_sample" or df_setting == "load_20_random_appended":
        df_setting = "load_csv"

    df = gen_df_climate_tweets(data_full_filepath, cli_kw_ff, setting = df_setting, 
        stopwords_changed = stopwords_changed, custom_stop = custom_stop) 


    ### RUN LDA ANALYSES ###

    lda_setting = "run_lda" # Options: run_lda, graph_coherence
    lda_logging = "terminal" # Options: terminal, file, None 
    num_topics = 5 # number of topics in LDA or max_range in graph_coherence, determined in run_lda by graph_coherence 
    passes = 3 # number of passes through the corpus, if a warning in log, need to increase

    run_lda_kwargs = {"extreme_low" : 0.0025, "extreme_high" : 0.25,
        "bigrams" : False, "trigrams" : False, "lda_example_print" : None, "viz" : True}

    graph_coherence_kwargs = {"range_min" : 1, "print_" : True}


    if lda_setting == "graph_coherence":
        lda_kwargs = deepcopy(graph_coherence_kwargs)

        tweets_coherence, coherence_winner = gen_lda_wrapper(
            df = df, tokenized_text_col = "tokenized_Tweet Text",
            lda_setting = lda_setting, lda_logging = lda_logging, 
            num_topics = num_topics, passes = passes, lda_save = None, **lda_kwargs 
            )

    elif lda_setting == "run_lda":
        lda_kwargs = deepcopy(run_lda_kwargs)
        
        lda_model, corpus, dictionary_LDA, lda_viz = gen_lda_wrapper(
            df = df, tokenized_text_col = "tokenized_Tweet Text",
            lda_setting = lda_setting, lda_logging = lda_logging, 
            num_topics = num_topics, passes = passes, lda_save = None, **lda_kwargs 
            )


    ### PRE-PROCESS LDA TOPIC DATA, PREDICTOR VARIABLE DATA, AND MERGE ### 

    if lda_setting == "run_lda":
        predictors_ff = "https://raw.githubusercontent.com/patrickncage/sample-public-repo/main/climate_tweet_LDA/example_data/Candidate_predictors_limited-gh-ex_11Oct21_cli-bool.csv"
        df_p_sample = pd.read_csv(predictors_ff)
    
    # remove missing data 
    df_p_sample.dropna(inplace=True) 

    # data pre-processing and merging together predictor and response variable datasets, now ready for regression
    df_merged =  lda_processing_results.gen_lda_by_author_regression_ready(lda_model, corpus, df, df_p_sample)



    ### RUN REGRESSIONS OVER DIFFERENT FRAMES AND PRINT TABLE OF RESULTS ### 

    expl_var_cols = ["Incumbent?", "Age", "Followers Count"]

    # can feed upper number from LDA_model 
    resp_var_cols = [(str(float(n)) + " Bool") for n in np.arange(0,num_topics,1)]

    # converts bools to 1 and 0, which statsmodels requires 
    for col in resp_var_cols:
        df_merged[col] = np.where(df_merged[col] == True, 1, 0)

    df_logit_models = logit_table_multi_response_var(df_merged, resp_var_cols, 
        expl_var_cols, bonferri_cxn = True, print_=True) 

    print(df_logit_models)


    if df_setting_print == "load_5_perc_sample":
        print("\nFrom this example model run on 5% of the data, it appears that all LDA topics \
do not vary significantly with respect to these variables.\n")
        print("This is not too surprising because of how we normalized the variables!\n")
        print("In practice, we might normalize each LDA Topic by all Climate Tweets by that \
candidate, rather than tweets of all subjects. Stay tuned for the academic manuscript to see \
those results!")