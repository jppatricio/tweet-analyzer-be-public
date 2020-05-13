import re ## PARA EXPRESIONES REGULARES
import tweepy ## Biblioteca para obtener los tweets
from tweepy import OAuthHandler ## OAtuh del API de Tweeter
from textblob import TextBlob 
import nltk
import os
from os import system
import pandas as pd

nltk.download('numpy')
import numpy

# We need this dataset in order to use the tokenizer
nltk.download('punkt')
from nltk.tokenize import word_tokenize

# Also download the list of stopwords to filter out
nltk.download('stopwords')
from nltk.corpus import stopwords

from nltk.stem.snowball import SnowballStemmer 
stemmer = SnowballStemmer('spanish')

from sklearn.feature_extraction.text import CountVectorizer
matrix = CountVectorizer(max_features=1000)

## INICIO DEL PROGRAMA
# creating object of TwitterClient Class 
api = ClienteTwitter()
# init arrays
tweets = []
listTweetsData = []
listTopics = []
querries = numpy.array([])

########################################
# init dataframe and read or create
df = pd.DataFrame({"Tweet":[],"Label":[]})
empty = False
exists = os.path.exists('cleanTweets.csv')

if(exists):
    try:
        df = pd.read_csv('cleanTweets.csv')
    except Exception as e:
        empty = True
else:
    print(df)
    df.to_csv(r'cleanTweets.csv', index=False)
    empty = True
########################################

########################################
########### ADD NEW DATA ############
addTweetsToCSV = input("¿Quieres ingresar nuevos tweets al csv?[y/n]").lower()

if(addTweetsToCSV == "y"):
    while(True):
        query = input("Ingresa un query (n para dejar de agregar): \n")
        if(query.lower() == "n"):
            break
        topic = input("Topico?: \n")
        q = Querry(query, topic)
        querries = numpy.append(querries, numpy.array(q))

    ## FETCHING TWEETS - SAVING THEM IN cleanTweets.csv
    index = 1
    system('clear') 
    print("Fetching tweets..............0.0%")
    for e in querries:
        tweets = api.get_tweets(query = e.query, count = 200)
        for tweet in tweets:
            stringTweets = ""
            for word in tweet['text']:
                stringTweets = stringTweets + word + " "
            listTweetsData.append(stringTweets)

        for tweet in tweets:
            listTopics.append(e.topic)
        system('clear') 
        print("Fetching tweets.............." + str(index/len(querries) * 100) + "%")
        index = index + 1
    ##

    ## ADDING DATA TO FILE
    newData = {"Tweet":[],"Label":[]}
    for tweet in listTweetsData:
        newData["Tweet"].append(tweet)
        
    for label in listTopics:
        newData["Label"].append(label)

    df2 = pd.DataFrame(newData)
    print(df2)
    # for appending df2 at the end of df1 
    df = df.append(df2, ignore_index = True, sort=False)
    print(df)
    df.to_csv(r'cleanTweets.csv', index=False)

print("\n - Converting Data... - \n")
listTweetsData = []
listTopics = []
for t in df['Tweet']:
    listTweetsData.append(t)
for t in df['Label']:
    listTopics.append(t)

########################################


########################################
############ TRAINING ###############

vectors = matrix.fit_transform(listTweetsData).toarray()

from sklearn.model_selection import train_test_split
vectors_train, vectors_test, topics_train, topics_test = train_test_split(vectors, listTopics, test_size=0.6)

# from sklearn.naive_bayes import GaussianNB
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import ComplementNB
# classifier = GaussianNB() # .34 Accuracy
# classifier = MultinomialNB() # .57 Accuracy
# classifier = BernoulliNB() #.47 Accuracy
classifier = ComplementNB() # .64 Accuracy
classifier.fit(vectors_train, topics_train)

# Predict with the testing set
topics_pred = classifier.predict(vectors_test)

# ...and measure the accuracy of the results
from sklearn.metrics import classification_report
print(classification_report(topics_test, topics_pred))

########################################
########################################

########################################
#             PREDICTIONS              #
########################################
while(True):
    newTweet = input("Tweet: ")
    Xnew = api.clean_tweet(newTweet)

    stringTweets = ""
    for word in Xnew:
        stringTweets = stringTweets + word + " "
    listTweetsData.append(stringTweets)


    vectors = matrix.fit_transform(listTweetsData).toarray()
    topics_pred = classifier.predict(vectors)

    arr = numpy.array([[topics_pred[len(topics_pred) - 1]]])

    print("Etiqueta asignada => " + str(arr[0]))
