from nltk.stem import SnowballStemmer, WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk



class DataPreprocessor:
    def __init__(self, language="english"):
        """
        Initializes the DataPreprocessor with a language for stopwords and stemmer/lemmatizer.

        :param language: Language for stopwords and stemmer (default: "english")
        """
        nltk.download("punkt_tab")
        nltk.download("stopwords")
        nltk.download("wordnet")

        self.stopwords = set(stopwords.words(language))
        self.stemmer = SnowballStemmer(language)
        self.lemmatizer = WordNetLemmatizer()


    def preprocess(self, text, remove_stopwords=True, stem=False, lemmatize=False):
        """
        Preprocesses plain text by optionally removing stopwords, stemming, or lemmatizing.

        :param text: Plain text to preprocess
        :param remove_stopwords: Whether to remove stopwords (default: True)
        :param stem: Whether to apply stemming (default: False)
        :param lemmatize: Whether to apply lemmatization (default: False)
        :return: Preprocessed plain text
        """
        if stem and lemmatize:
            raise ValueError("Cannot apply both stemming and lemmatization. Choose one.")

        # Tokenize the input text
        tokens = word_tokenize(text)

        # Apply preprocessing steps
        if remove_stopwords:
            tokens = self.__remove_stopwords(tokens)
        if stem:
            tokens = self.__stem_tokens(tokens)
        if lemmatize:
            tokens = self.__lemmatize_tokens(tokens)

        # Join tokens back into plain text
        cleaned_text = " ".join(tokens)
        return cleaned_text

    def __remove_stopwords(self, tokens):
        """
        Removes stopwords from a list of tokens.

        :param tokens: List of tokens
        :return: Tokens without stopwords
        """
        return [token for token in tokens if token.lower() not in self.stopwords]

    def __stem_tokens(self, tokens):
        """
        Applies stemming to tokens.

        :param tokens: List of tokens
        :return: Stemmed tokens
        """
        return [self.stemmer.stem(token) for token in tokens]

    def __lemmatize_tokens(self, tokens):
        """
        Applies lemmatization to tokens.

        :param tokens: List of tokens
        :return: Lemmatized tokens
        """
        return [self.lemmatizer.lemmatize(token) for token in tokens]