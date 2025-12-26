from rest_framework import serializers
from crawler_soup.models import SubredditPost

class SubredditsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubredditPost
        fields = '__all__'