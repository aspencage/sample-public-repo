# sample-public-repo
**Description**: This is a personal public repo containing samples of code, intended primarily for sharing with potential future collaborators. Repo author has rights to all code included here. Most code written between June 2021 and the present date is IP owned externally, and therefore none of this code is included.


### Directory: blackjack (may 2023)

**Description**: Python scripts that can be used to simulate the odds of winning in a simplified version of the card game Blackjack, given a particular starter hand. The program will simulate probabilities and suggest whether you should hit (draw a card) or stay (not draw a card) for the best chance of winning. `blackjack.py` contains the game engine. `gui.py` contains a Graphical User Interface usable by anyone running Python 3. 

**Demonstrates**: object-oriented programming (OOP) for both simulation (`blackjack.py`) and interactivity (`gui.py`).

**Package requirements**: `numpy`, otherwise all builtin packages.

**Todo**: remaining planned updates to this living script include: allowing user to see one of dealer's cards, allowing dealer to draw, a simple Python-launched GUI version, a web hosted GUI version, increased object orientation. 

 *Last updated*: 25 May 2023


### Directory: shell-scripting (may 2023)

**Description**: A set of Shell scripts to support the use of a cloud-based supercomputer (AWS EC2 GPU instance). `orbweave.sh` in particular provides a set of simple wrapper functions to "turnkey" interact with their instance, allowing them to spend more time running analysis and less on instance management.

**Demonstrates**: shell scripting/command line, efficient helper functions.

**Package requirements**: This should work in any UNIX terminal. Actual use will require adding AWS EC2 on-demand Instance ID and Security Group ID to `config_ow.sh` and having authenticated in the AWS Command Line Interface. 

*Last updated*: 21 May 2023



### Directory: technoeconomic-simulator (nov 2021)

**Description**: Python snippets arbitrary selected from a technoeconomic simulator package, developed while learning the principles of object-oriented programming. `fluxes.py` and `some_parts.py`, in particular, contain several simple classes, as examples. 

**Demonstrates**: object-oriented programming (OOP).



### Directory: climate-ml-text-analysis (june 2021)

**Description**: Python scripts developed for topic modeling of Twitter posts by down-ballot political candidates during the 2020 election cycle. 

These scripts and sample data are a small example from ongoing academic research into candidate issue messaging. This can be run out of the box with the `lda_set_and_run.py script`, which will run a Latent Dirichlet Machine topic model and perform logistic regressions for all topics found using example predictors. A command line prompt (printed in the code) may be required to experience the interactive LDA results because of a known issue in gensim. Additional sample of statistics in the `__name__ == '__main__'` code block of `lda_processing_results.py`.

**Demonstrates**: machine learning models, regression models, exploratory statistics, text-to-data/content analysis, data gymnastics.

**Package requirements**: `gensim == 4.0.1`, `statsmodels == 0.12.2`, and `nltk == 3.6.1` are required packages that may not already be installed in your Python environment.

**Future updates**: Potential to provide a more thorough analysis from real data with a dummy political issue (e.g., coffee, puppies), rather than investigating for climate here, where pre-publication data protections are necessary.



### Directory: dashboard-data-mgmt (sep 2020)

**Description**: A pipeline of Python scripts developed as a practical approach to clean and merge data lacking common ID system. Applied for periodic data upload to Google Sheets during a fast-paced 2020 election cycle collaboration. 

**Demonstrates**: Data processing (cleaning, transforming, merging) and automated uploading via API.


### *Repo Under Construction*
This is a sporadically-updated GitHub repository. More example code will continue to be added over time and can be shared bilaterally on request. 
