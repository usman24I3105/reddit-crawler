from rest_framework.views import APIView
from rest_framework.response import Response
from crawler_soup.api.serializers import SubredditsSerializer
from crawler_soup.models import SubredditPost
from .task import getposts
from rest_framework.permissions import IsAuthenticated


class SubredditsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        queryset = SubredditPost.objects.all()

        serializer = SubredditsSerializer(queryset, many=True)

        return Response(serializer.data)