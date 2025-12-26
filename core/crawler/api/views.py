from rest_framework.views import APIView
from rest_framework.response import Response
from praw import Reddit
from crawler.api.serializers import SubredditPostSerializer
from crawler.models import SubredditPost
from datetime import datetime
from env import REDDIT_CLIENT_ID,REDDIT_CLIENT_SECRET,REDDIT_USER_AGENT

class SubredditPostViewPraw(APIView):
    def get(self, request, format=None):
        # Reddit API istemcisini oluşturuyorum
        reddit = Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET,
                        user_agent=REDDIT_USER_AGENT)
        
        subreddit = 'Home'

        # Subredditten son 10 postu alıyorum
        posts = reddit.subreddit(subreddit).new(limit=30)

        # Her post için SubredditPost nesnesi oluşturup ve veritabanına kaydediyorum
        for post in posts:
            existing_post = SubredditPost.objects.filter(title=post.title, subreddit=subreddit).exists()
            if not existing_post:
                created_utc = datetime.utcfromtimestamp(post.created_utc)
                subreddit_post = SubredditPost(
                    title=post.title,
                    author=post.author.name,
                    created_utc=created_utc,
                    url=post.url,
                    subreddit=subreddit
                )
                subreddit_post.save()

        # Veritabanındaki tüm SubredditPost nesnelerini alıyorum
        queryset = SubredditPost.objects.all()

        # Serializer'ı kullanarak verileri JSON formatına dönüştürüyorum
        serializer = SubredditPostSerializer(queryset, many=True)

        return Response(serializer.data)