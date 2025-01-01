def tokenize_text(text):
    """
    Tokenizes the text into individual words.

    :param text: Cleaned text
    :return: List of tokens
    """
    return text.split()


def remove_stopwords(tokens, stopwords):
    """
    Removes stopwords from a list of tokens.

    :param tokens: List of tokens
    :param stopwords: List of stopwords
    :return: Tokens without stopwords
    """
    return [token for token in tokens if token.lower() not in stopwords]


def stem_tokens(tokens, stemmer):
    """
    Applies stemming to tokens.

    :param tokens: List of tokens
    :param stemmer: A stemmer instance (e.g., from NLTK or SnowballStemmer)
    :return: Stemmed tokens
    """
    return [stemmer.stem(token) for token in tokens]


def lemmatize_tokens(tokens, lemmatizer):
    """
    Applies lemmatization to tokens.

    :param tokens: List of tokens
    :param lemmatizer: A lemmatizer instance (e.g., WordNetLemmatizer)
    :return: Lemmatized tokens
    """
    return [lemmatizer.lemmatize(token) for token in tokens]


'''
def preprocess_data(cleaned_text, stopwords, stemmer=None, lemmatizer=None):
    """
    Preprocesses cleaned text by tokenizing, removing stopwords, and applying stemming/lemmatization.

    :param cleaned_text: Text after cleaning
    :param stopwords: List of stopwords
    :param stemmer: Optional stemmer instance
    :param lemmatizer: Optional lemmatizer instance
    :return: Processed tokens
    """
    # Step 1: Tokenize text
    tokens = tokenize_text(cleaned_text)

    # Step 2: Remove stopwords
    tokens = remove_stopwords(tokens, stopwords)

    # Step 3: Apply stemming or lemmatization
    if stemmer:
        tokens = stem_tokens(tokens, stemmer)
    elif lemmatizer:
        tokens = lemmatize_tokens(tokens, lemmatizer)

    return tokens
'''