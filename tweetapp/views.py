from django.contrib.auth.models import User, Group
from rest_framework import viewsets, response
from tweetapp.serializers import UserSerializer, GroupSerializer, TweetSerializer
from tweetapp.models import TweetLabelerRequestModel
from django.http import Http404
from rest_framework.response import Response
from rest_framework import serializers, views

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings
import json


import re ## PARA EXPRESIONES REGULARES
import tweepy ## Biblioteca para obtener los tweets
from tweepy import OAuthHandler ## OAtuh del API de Tweeter
import pickle
from textblob import TextBlob 
import nltk
import os
from os import system
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
matrix = CountVectorizer(max_features=10000)


from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import ComplementNB


from collections import namedtuple

from tweetapp.clienteTwitter import ClienteTwitter, Querry
import numpy


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TweetViewSet(viewsets.ModelViewSet):

    queryset = TweetLabelerRequestModel.objects.all()
    serializer_class = TweetSerializer

@api_view(["POST"])
def getLabel(request):
    api = ClienteTwitter()
    data = json.loads(request.body)
    tweet = data['tweet']
    password = data['password']
    if(password != ""):     #Change Password if needed
        return JsonResponse("WRONG PASSWORD", safe=False)
    model = data['model']
    switcher = {
        1: "GaussianNB",
        2: "MultinomialNB",
        3: "BernoulliNB",
        4: "ComplementNB",
        }
    model_name = switcher.get(model, "ComplementNB")
    path = os.path.join(settings.MODEL_ROOT, model_name)
    try:
        with open(path, 'rb') as file:
            model = pickle.load(file)
    except:
        return Response("Se ingresó un modelo inexistente...", status=500)
    path = os.path.join(settings.MODEL_ROOT, model_name + "-arr")
    with open(path, 'rb') as f:
        listTweetsData = pickle.load(f)
    Xnew = api.clean_tweet(tweet)
    stringTweets = ""
    for word in Xnew:
        stringTweets = stringTweets + word + " "
    listTweetsData.append(stringTweets)
    vectors = matrix.fit_transform(listTweetsData).toarray()
    try:
        topics_pred = model.predict(vectors)
        arr = numpy.array([[topics_pred[len(topics_pred) - 1]]])
        jsonResponse = {"label" : str(arr[0])}
        return Response(jsonResponse, status=status.HTTP_200_OK)
    except:
        return Response("Se ingresó una palabra incorrecta o inexistente...", status=500)
    
    return Response({"FINISHED INCORRECTLY" : "???"}, status=404)

    
class Train(views.APIView):
    def post(self, request):
        data = json.loads(request.body)
        model = data['model']
        password = data['password']
        testSize = data['testSize']
        topics = data['topics']
        if(password != ""):     #Change Password if needed
            return JsonResponse("WRONG PASSWORD", safe=False)
        
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
        exists = os.path.exists(os.path.join(settings.BASE_DIR, 'cleanTweets.csv'))
        if(exists):
            try:
                df = pd.read_csv(os.path.join(settings.BASE_DIR, 'cleanTweets.csv'))
                
            except Exception as e:
                return Response("COULDNT READ FILE", status=500)
        else:
            return Response("CSV DOES NOT EXIST", status=404)
        
        
        ########################################
        ########################################
        if(len(topics) != 0 ):
            
            print("Fetching tweets.............. 0%")
            for item in topics:
                topic = item
                q = Querry(topic, topic)
                querries = numpy.append(querries, numpy.array(q))

            ## FETCHING TWEETS - SAVING THEM IN cleanTweets.csv
            index = 1
            system('clear') 
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
            df = pd.DataFrame(newData)

        ########################################
        ########################################
        print("\n - Converting Data... - \n")
        print(df)
        listTweetsData = []
        listTopics = []
        for t in df['Tweet']:
            listTweetsData.append(t)
        for t in df['Label']:
            listTopics.append(t)
        
        modelType = {
        1: "GaussianNB",
        2: "MultinomialNB",
        3: "BernoulliNB",
        4: "ComplementNB", 
        }
        
        path = os.path.join(settings.MODEL_ROOT, modelType.get(model, "ComplementNB") + "-arr")
        with open(path, 'wb') as file:
            pickle.dump(listTweetsData, file)
        ########################################
        ############ TRAINING ###############

        vectors = matrix.fit_transform(listTweetsData).toarray()

        from sklearn.model_selection import train_test_split
        vectors_train, vectors_test, topics_train, topics_test = train_test_split(vectors, listTopics, test_size=testSize)
        switcher = {
        1: GaussianNB(),
        2: MultinomialNB(),
        3: BernoulliNB(),
        4: ComplementNB(),
        }
        classifier = switcher.get(model, ComplementNB())
        classifier.fit(vectors_train, topics_train)

        # Predict with the testing set
        topics_pred = classifier.predict(vectors_test)

        # ...and measure the accuracy of the results
        from sklearn.metrics import classification_report
        print(classification_report(topics_test, topics_pred))
        path = os.path.join(settings.MODEL_ROOT, modelType.get(model, "ComplementNB"))
        with open(path, 'wb') as file:
            pickle.dump(classifier, file)
        jsonResponse = pd.DataFrame(classification_report(topics_test, topics_pred, output_dict=True))
        return Response(jsonResponse, status=status.HTTP_200_OK)
