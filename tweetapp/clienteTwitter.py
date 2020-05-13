import re ## PARA EXPRESIONES REGULARES
import tweepy ## Biblioteca para obtener los tweets
from tweepy import OAuthHandler ## OAtuh del API de Tweeter
from textblob import TextBlob 
import nltk
import os
from os import system
import pandas as pd

# nltk.download('numpy')
import numpy
# We need this dataset in order to use the tokenizer
# nltk.download('punkt')
from nltk.tokenize import word_tokenize
# Also download the list of stopwords to filter out
# nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer 
stemmer = SnowballStemmer('spanish')
from sklearn.feature_extraction.text import CountVectorizer
matrix = CountVectorizer(max_features=1000)

class ClienteTwitter(object): 

###############################################
## INICIALIZACION PARA LA AUTENTICACION DEL API
###############################################
    def __init__(self): 
        # keys and tokens from the Twitter Dev Console 
        consumer_key = '***************************'
        consumer_secret = '***************************'
        access_token = '***************************'
        access_token_secret = '***************************'

        self.otrosPorEliminar = ['@', 'rt', 'http', 'com']
  
        # attempt authentication 
        try: 
            # create OAuthHandler object 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            # set access token and secret 
            self.auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 


        except: 
            print("Error: Authentication Failed") 

###############################################
## TERMINA LA INICIALIZACION PARA LA AUTENTICACION DEL API
###############################################


###############################################
# FUNCION PARA LIMPIAR EL TWEET
###############################################
  
    def clean_tweet(self, tweet): 
        # cleanTweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
        # Make all the strings lowercase and remove non alphabetic characters
        tweet = re.sub('[^a-zA-Z\u00C0-\u00FF]+', ' ', tweet.lower())

        # Tokenize the tweet; this is, separate every sentence into a list of words
        # Since the tweet is already split into sentences you don't have to call sent_tokenize
        tokenized_tweet = word_tokenize(tweet)
        # Elimina usuario y RT
        tokenized_tweet = tokenized_tweet[1:]

        # Remove the stopwords and stem each word to its root
        clean_tweet = [
            stemmer.stem(word) for word in tokenized_tweet
            if word not in stopwords.words('spanish')
            and word not in self.otrosPorEliminar
        ]

        # Remember, this final output is a list of words
        return clean_tweet

###############################################
# FUNCION PARA OBTENER LOS TWEETS SEGUN SU QUERY
###############################################
    def get_tweets(self, query, count): 
        ''' 
        Main function to fetch tweets and parse them. 
        '''
        # empty list to store parsed tweets 
        tweets = [] 
  
        try: 
            # print("FETCHING")
            # call twitter api to fetch tweets 
            fetched_tweets = self.api.search(q = query, count = count, lang='es') 
            # print("FETCHED")
  
            # parsing tweets one by one 
            for tweet in fetched_tweets: 
                # empty dictionary to store required params of a tweet 
                parsed_tweet = {} 
  
                # saving text of tweet 
                parsed_tweet['text'] = [" ".join(self.clean_tweet(tweet.text))]
                # self.clean_tweet(tweet.text)
  
                # appending parsed tweet to tweets list 
                if tweet.retweet_count > 0: 
                    # if tweet has retweets, ensure that it is appended only once 
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet) 
                else: 
                    tweets.append(parsed_tweet) 
  
            # return parsed tweets 
            return tweets 
  
        except tweepy.TweepError as e: 
            # print error (if any) 
            print("Error : " + str(e))


###############################################
# FIN DE LA CLASE ClienteTwitter
###############################################

class Querry(object):
    query = ""
    topic = ""
    def __init__(self, q, t):
        self.query = q
        self.topic = t