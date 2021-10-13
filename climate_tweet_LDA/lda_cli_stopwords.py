# lda_cli_stopwords

custom_generic_stop = ["amp", "texan", "tx", "rep", "&amp;", "dont", "don't", "must", "get",
    "that", "may", "district", "join", "see", "us", "today", "day", "pm", "make",
    "support", "take", "full", "need", "talk", "austin", "copolitics", "txlege", "ncpol",
    "get", "part", "th", "bring", "ca25", "test", "use", "include", "including", "look", "state",
    "im", "ive", "ill", "late", "day", "go", "got", "one", "also", "ago", "via",
    "that", "like", "cant", "bring", "thing", "see", "year", "isnt",
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", 
    "delaware", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", 
    "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", 
    "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", 
    "new hampshire", "new jersey", "new mexico", "new york", "north carolina", "north dakota", 
    "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota", 
    "tennessee", "texas", "utah", "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming",
    'al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'dc', 'de', 'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia', 'ks', 'ky', 
    'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj', 'nm', 'ny', 'nc', 'nd', 'oh', 
    'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt', 'va', 'wa', 'wv', 'wi', 'wy']

climate_stop = ["climate", "climatechange", "crisis", "fight", "time", "year", "whether", "much", "action", 
    "let", "times", "timing", "want", "wanted", "wants", "wanting", "big", "bigger", "biggest", "check", 
    "checking", "checked", "people", "peoples", "timer", "timed", "crises", "crisises", "fought", "fighting",
    "think", "help", "change"]

custom_subject_stop =  climate_stop

custom_stop = custom_generic_stop + custom_subject_stop