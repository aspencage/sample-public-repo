# lda_climate_gensim

''' 
functions for practical LDA in gensim implemented to analyze climate change Tweets
'''

import os
import re
import json
import requests  
import random 
from datetime import datetime
from math import log10, floor
from glob import glob
import pandas as pd

from nltk import download as nltk_dl
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer

from gensim.models.phrases import Phrases, ENGLISH_CONNECTOR_WORDS
from gensim import corpora, models

import pyLDAvis
import pyLDAvis.gensim_models 

import matplotlib.pyplot as plt 

from glob_minus_glob import glob_minus_glob

# for progress counting
def round_to_n(x, n):
    return round(x, -int(floor(log10(x))) + (n - 1))


def subset_and_preprocess_tweets(
    df,
    tweet_col = "Tweet Text",
    date_col="Tweet Timestamp",
    start_dt = None,
    end_st = None,
    keyword_exp = None,
    custom_stop = None):

    df_copy = df.copy()

    # format the date 
    df_copy[date_col] = df_copy[date_col].apply(lambda row: datetime.strptime(
        row, "%Y-%m-%d %H:%M:%S"))

    # constrain to election cycle, here 1 year 
    if start_dt:
        df_copy = df_copy[df_copy[date_col] >= start_dt]
    if end_st:
        df_copy = df_copy[df_copy[date_col] <= end_st]

    # lower the tweets
    df_copy["preprocessed_" + tweet_col] = df_copy[tweet_col].str.lower()

    # remove punctuation
    p = re.compile(r'[^\w\s]+')
    df_copy["preprocessed_" + tweet_col] = [p.sub('', x) for x in df_copy["preprocessed_" + tweet_col].tolist()]

    if keyword_exp:
        mask = df_copy["preprocessed_" + tweet_col].str.contains(keyword_exp, na=False, case=False)
        df_copy = df_copy.loc[mask]

    # filter out stopwords and urls 
    try:
        en_stop_words = stopwords.words("english")
    except LookupError:
        nltk_dl("stopwords")
        en_stop_words = stopwords.words("english")

    if custom_stop:
        en_stop_words.extend(custom_stop)

    # original url_re = r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})'
    # modified to remove urls bc now no punctuation
    url_re = r'(httpstco)[a-zA-Z0-9][a-zA-Z0-9-]+'

    # remove usernames
    at_re = r"@[a-z]*"
    df_copy['preprocessed_' + tweet_col] = df_copy['preprocessed_' + tweet_col].apply(
        lambda row: ' '.join([word for word in row.split() if (
            not word in en_stop_words) and (not re.match(url_re, word)) and (not re.match(at_re, word))]))

    return df_copy


#  tokenizing, stemming or lemmatizing
def token_and_stem_tweets(
    df,
    tweet_col = "Tweet Text",
    stem_or_lem = "lem"
    ):

    df_copy = df.copy()

    # tokenize the tweets
    tokenizer = RegexpTokenizer(r"[a-zA-Z]\w+\'?\w*")
    stemmer = SnowballStemmer("english")
    lemmatizer = WordNetLemmatizer()

    df_copy.dropna(subset=["preprocessed_"+ tweet_col], inplace=True)

    if stem_or_lem == "lem":
        try:
            df_copy["tokenized_" + tweet_col] = df_copy["preprocessed_" + tweet_col].apply(
                lambda row: [lemmatizer.lemmatize(token) for token in tokenizer.tokenize(row)]
                )
        except LookupError:
            nltk_dl("wordnet")
            df_copy["tokenized_" + tweet_col] = df_copy["preprocessed_" + tweet_col].apply(
                lambda row: [lemmatizer.lemmatize(token) for token in tokenizer.tokenize(row)]
                )
    elif stem_or_lem == "stem":

        try:
            df_copy["tokenized_" + tweet_col] = df_copy["preprocessed_" + tweet_col].apply(
                lambda row: [stemmer.stem(token) for token in tokenizer.tokenize(row)]
                )

        except LookupError:
            nltk_dl("wordnet")
            df_copy["tokenized_" + tweet_col] = df_copy["preprocessed_" + tweet_col].apply(
                lambda row: [stemmer.stem(token) for token in tokenizer.tokenize(row)]
                )

    return df_copy


def gen_df_climate_tweets(data_full_filepath: str, cli_kw_ff: str,
    setting: str = "load_csv", start_dt:datetime=datetime(2019,11,3,0,0,0), 
    end_st:datetime=datetime(2020,11,3,0,0,0), stopwords_changed:bool = False, custom_stop:list = None):
    """Loads/generates a pd.DataFrame and preprocesses it to be ready for LDA.

    Args:
        data_full_filepath (str): 
        cli_kw_ff (str): Filepath to the JSON file with keywords to mark a Tweet as relevant.
        setting (str, optional): Approach to use to retrieve data. Options: "load_20_random_appended", "load_5_perc_sample", "process_5_percent_sample", "process_corpus_new", "load_dir", "load_csv". GitHub code is ready out-of-the-box for load_20_random_appended and load_5_perc_sample. Other options require user to provide own data. Defaults to "load_csv".
        start_dt (datetime, optional): Beginning of Tweet date range to include. Defaults to datetime(2019,11,3,0,0,0).
        end_st (datetime, optional): End of Tweet date range to include. Defaults to datetime(2020,11,3,0,0,0).
        stopwords_changed (bool, optional): Indicate whether the stopwords have changed since exporting a processed dataset, if loading a csv dataset. Defaults to False.
        custom_stop (list, optional): List of stopwords to consider when re-processing if stopwords_changed == True. Defaults to None.

    Raises:
        ValueError: Setting is enforced. 

    Returns:
        pd.DataFrame: pd.DataFrame ready for LDA analysis. 
    """

    if re.compile("http").search(cli_kw_ff): # for URLs
        keyword_list = requests.get(cli_kw_ff).json()
        print("YAAAAY")
    else:
        with open(cli_kw_ff, "r") as file:
            keyword_list = json.load(file)
    keyword_exp = ("|".join(keyword_list))

    ff = data_full_filepath

    if setting == "load_dir":
    # (1) load tweets prepopulated into a folder 
        os.chdir(ff)
        csvs = glob("*.csv")

        # compile df of all tweets
        for csv in csvs:
            temp_df = pd.read_csv(csv)
            try:
                df = df.append(temp_df)
            except NameError:
                df = temp_df

        print("pre subset/process df length:", df.shape[0])
        df = subset_and_preprocess_tweets(
            df, 
            start_dt=start_dt,
            end_st=end_st, 
            keyword_exp=keyword_exp,
            custom_stop=custom_stop) 
        print("post subset/process df length:", df.shape[0])

    # (2) read from a csv dataset 
    elif setting == "load_csv":
        df = pd.read_csv(ff)

    elif setting == "process_5_percent_sample" or setting == "process_corpus_new":
        allglob="**/*all tweet*"
        minusglob1 = "*Rep*/**/*all tweet*" # "*Dem*/**/*all tweet*" # need to add /**/ for Dem bc of different file structure 
        minusglob2 = "*Biden*/*all tweet*"
        minusglob3 = "*Legislative*/**/*all tweet*"
        fps = glob_minus_glob(ff, allglob, 
            minusglob1, minusglob2, minusglob3)

        i = 0
        one_percent_done = len(fps)/100
        one_percent_done_digits = int(log10(one_percent_done)) + 1
        rounded_total = round_to_n(len(fps), one_percent_done_digits + 1)
        one_percent_done = int(floor(one_percent_done))
    
        # generate 5% of Tweets from all (Dem) candidates 
        if setting == "process_5_percent_sample":
            p = 0.05  # proportion of the lines to use
            # if random from [0,1] interval is greater than p the row will be skipped
            for csv in fps:
                temp_df = pd.read_csv(csv, skiprows=lambda i: i>0 and random.random() > p) 
                try:
                    df = df.append(temp_df)
                except NameError:
                    df = temp_df
                # progress monitor
                i += 1

                if i % one_percent_done  == 0:
                    print(f"Approx. {int(floor(i/rounded_total*100))}% complete, {i} files read")

            print("pre subset/process df length:", df.shape[0])
            df = subset_and_preprocess_tweets(
                df, 
                start_dt=start_dt,
                end_st=end_st, 
                keyword_exp=keyword_exp,
                custom_stop=custom_stop)
            print("post subset/process df length:", df.shape[0])

        elif setting == "process_corpus_new":
            # process as we go option here to avoid overwhelming computer memory
            for csv in fps:
                temp_df = pd.read_csv(csv)  
                try:
                    temp_df = subset_and_preprocess_tweets(
                        temp_df, 
                        start_dt=start_dt,
                        end_st=end_st, 
                        keyword_exp=keyword_exp,
                        custom_stop=custom_stop)
                except AttributeError:
                    continue
                try:
                    df = df.append(temp_df)
                except NameError:
                    df = temp_df
                # progress monitor
                i += 1

                if i % one_percent_done  == 0:
                    print(f"Approx. {int(floor(i/rounded_total*100))}% complete, {i} files read")

            print(f"100% complete, {i} files read.")

    else:
        raise ValueError(f"{setting} is not an allowable setting. see code for options.")

    if stopwords_changed == True:
        df = subset_and_preprocess_tweets(
            df, 
            start_dt=start_dt,
            end_st=end_st, 
            keyword_exp=keyword_exp,
            custom_stop=custom_stop)
        print("Re-processed stopwords from data file")

    df = token_and_stem_tweets(df)

    return df 


def visualize_lda(lda_model, corpus, dictionary_LDA):
    vis = pyLDAvis.gensim_models.prepare(
        topic_model=lda_model,
        corpus=corpus,
        dictionary=dictionary_LDA,
        sort_topics = False)
    pyLDAvis.enable_notebook(local=True)
    pyLDAvis.display(vis)

    print("\n\n~NOTE~")
    print("If interactive LDA visualization is not displaying in your interpreter,")
    print("force display with >>> pyLDAvis.display(lda_viz)\n\n")

    return vis

def run_lda(df:pd.DataFrame, tokenized_text_col:str = "tokenized_Tweet Text", 
    num_topics:int=20, extreme_low:float = 0.0025, extreme_high:float = 0.25,
    passes:int=4, bigrams:bool=False, trigrams:bool=False,
    lda_example_print:str = None, viz:bool = True):


    list_of_list_of_tokens = df[tokenized_text_col].to_list()
    # because csv->Pandas can't handle lists

    # NOTE - CONSTRUCTION ZONE 
    if bigrams == True:
        # i believe this is right location, run after stem/lemmatiz-ing
        # https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html
        bigram = Phrases(list_of_list_of_tokens, min_count=20, connector_words=ENGLISH_CONNECTOR_WORDS)
        for idx in range(len(list_of_list_of_tokens)):
            for token in bigram[list_of_list_of_tokens[idx]]:
                if '_' in token:
                    # if token is a bigram, add to document.
                    list_of_list_of_tokens[idx].append(token)

        print("bigram \n", bigram)
        if trigrams == True: 
            # NOTE construction zone 
            # https://tedboy.github.io/nlps/_modules/gensim/models/phrases.html
            trigram = Phrases(bigram[list_of_list_of_tokens], min_count=20, connector_words=ENGLISH_CONNECTOR_WORDS)
            for idx in range(len(list_of_list_of_tokens)):
                for token in trigram[bigram[list_of_list_of_tokens[idx]]]:
                    if '_' in token:
                        if token.count("_") < 3:
                            # if token is a bigram, add to document.
                            list_of_list_of_tokens[idx].append(token)

            print("trigram \n", trigram)

    dictionary_LDA = corpora.Dictionary(list_of_list_of_tokens)
    dictionary_LDA.filter_extremes(no_below=extreme_low, no_above=extreme_high)
    corpus = [dictionary_LDA.doc2bow(list_of_tokens) for list_of_tokens in list_of_list_of_tokens]

    lda_model = models.LdaModel(corpus, num_topics=num_topics, \
                    id2word=dictionary_LDA, \
                    passes=passes, alpha="auto", \
                    eta="auto") # alt approach: alpha=[0.01]*num_topics, eta=[0.01]*len(dictionary_LDA.keys())

    # corpus corresponds to the tweet df index (as long as no shuffling) 
    if lda_example_print is not None:
        if lda_example_print == "topics":
            for i,topic in lda_model.show_topics(formatted=True, num_topics=num_topics, num_words=15):
                print(str(i)+": "+ topic)
                print()

        elif lda_example_print == "sample":
            # lda_model[corpus[0]] prints the topics involved in the first document 
            # get 50 random Tweets between 0 and df.shape[0]
            num_random_tweets=50
            random_tweets = random.sample(range(df.shape[0]),num_random_tweets) 
            for tweet_i in random_tweets:
                print("df Tweet index:", tweet_i)
                print(df["Tweet Text"].iloc[tweet_i])
                print(lda_model[corpus[tweet_i]])
                print()

    return lda_model, corpus, dictionary_LDA
    

def graph_coherence(df, tokenized_text_col, range_min = 1, range_max=35, 
    passes = 10, print_=True):
    # dict for each tweet 
    tweets_dictionary = corpora.Dictionary(df[tokenized_text_col])

    # build the corpus - vectors with the number of occurence of each word per tweet
    tweets_corpus = [tweets_dictionary.doc2bow(tweet) for tweet in df[tokenized_text_col]]

    # compute coherence
    tweets_coherence = []
    for nb_topics in range(range_min,range_max+1):
        if print_==True:
            print(f"testing coherence for {nb_topics} topics")
        lda = models.LdaModel(tweets_corpus, num_topics=nb_topics, 
            id2word = tweets_dictionary, passes = passes)
        cohm = models.CoherenceModel(model=lda, corpus=tweets_corpus, 
            dictionary=tweets_dictionary, coherence="u_mass")
        coh = cohm.get_coherence()
        tweets_coherence.append(coh)

    # visualize coherence
    plt.figure(figsize=(10,5))
    plt.plot(range(range_min,range_max+1), tweets_coherence)
    plt.xlabel("Number of topics")
    plt.ylabel("Coherence Score")

    plt.show()

    coherence_winner = tweets_coherence.index(min(tweets_coherence)) + 1

    if print_==True:
        print(tweets_coherence)
        print(f"The optimal number of topics for LDA from the perspective of coherence score \
is: {coherence_winner}. It is recommended the user visualizally evaluate the result.")
        if coherence_winner > len(tweets_coherence):
            print("However, the optimal coherence is the largest number of topics evaluated \
suggesting either range_max should be increased or the corpus processed (e.g., more common \
words removed from analysis).")

    return tweets_coherence, coherence_winner


def gen_lda_wrapper(df: pd.DataFrame, tokenized_text_col: str = "tokenized_Tweet Text",
    lda_setting:str = "run_lda", lda_logging:str = None, 
    num_topics:int = 35, passes:int = 3, lda_save:str = None, **kwargs):
    """Wrapper-style function to simplify LDA analysis from user perspective. \
Options for both running the LDA analysis and graphing coherence to determine the \
optimal number of topics for the model to development, given the data.

    Args:
        df (pd.DataFrame): Data pre-processed by gen_df_climate_tweets().
        tokenized_text_col (str, optional): Column containing the tokenized (and stemmed or lemmatized) Tweet Text. Defaults to "tokenized_Tweet Text".
        lda_setting (str, optional): Run LDA ("run_lda") or graph coherence ("graph_coherence"). Defaults to "run_lda".
        lda_logging (str, optional): Run LDA logs in terminal ("terminal") or save to designated file ("file"). Defaults to "terminal".
        num_topics (int, optional): Number of topics in LDA or max_range in graph_coherence. Defaults to 35.
        passes (int, optional): Number of passes through the corpus, if a warning in log, need to increase. Defaults to 3.
        lda_save (str, optional): Send a path if you want to export the LDA model. Defaults to None.

    Returns:
        run_lda returns lda_model, corpus, dictionary_LDA
        lda_model: The LDA model instance.
        corpus: The corpus around which the LDA model is built and which can be nested within lda_model to get document topic scores.
        dictionary_LDA: The dictionary from which the LDA model is built. 
        graph_coherence returns tweets_coherence, coherence_winner
        tweets_coherence (list): The coherence score calculated for each numer of topic runs. 
        coherence_winner (int): The number of topics with the optimal coherence score from the range analyzed.
    """

    # ENABLE LOGGING 
    import logging
    if lda_logging == "file":
    # to filename

        logging.basicConfig(
            filename='lda_model.log', 
            format='%(asctime)s : %(levelname)s : %(message)s', 
            level=logging.INFO)

    elif lda_logging == "terminal":
        # to terminal
        logging.basicConfig(
            format='%(asctime)s : %(levelname)s : %(message)s', 
            level=logging.INFO)

    elif lda_logging == None:
        logging.getLogger("imported_module").setLevel(logging.WARNING)

    else: 
        raise ValueError(f"{lda_logging} is not a valid selection for lda_logging. see code for options.")

    if lda_setting == "graph_coherence":

        tweets_coherence = graph_coherence(
            df=df, 
            tokenized_text_col=tokenized_text_col, 
            passes=passes,
            range_max=num_topics,
            **kwargs)

        return tweets_coherence


    elif lda_setting == "run_lda":
        # run the LDA with a selected number of topics 

        lda_model, corpus, dictionary_LDA = run_lda(
            df, 
            num_topics=num_topics,
            passes=passes,
            **kwargs)

        if lda_save is not None:
            from gensim.test.utils import datapath

            os.chdir(lda_save)
            temp_file = datapath("model")
            lda_model.save(temp_file)
            print("lda model saved")

        viz = kwargs["viz"]
        if viz == True:
            lda_viz = visualize_lda(lda_model, corpus, dictionary_LDA)
        else: 
            lda_viz = None

        return lda_model, corpus, dictionary_LDA, lda_viz


if __name__ == "__main__": 

    pass 