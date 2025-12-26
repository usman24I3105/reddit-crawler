from rest_framework import serializers
from crawler.models import SubredditPost

class SubredditPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubredditPost
        fields = '__all__'
