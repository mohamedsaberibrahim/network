from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from time import strftime

class User(AbstractUser):
    following = models.ManyToManyField('network.User', blank=True, related_name="followers")
    
    
    def likes(self, likes):
        for like in likes:
            if like.user == self:
                return True
        return False

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    body = models.TextField()
    timestamp = models.DateTimeField(default=now, editable=False)
    likeCount = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"{self.body} By: {self.user}"

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "user_id": self.user.id,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes" : self.likeCount
        }


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
