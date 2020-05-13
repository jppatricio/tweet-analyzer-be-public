from django.contrib.auth.models import User, Group
from rest_framework import serializers
from tweetapp.models import TweetLabelerRequestModel


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class TweetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TweetLabelerRequestModel
        fields = '__all__'