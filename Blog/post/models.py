from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()
# Create your models here.
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='authorImages/')

    def __str__(self):
        return self.user.username
class Category(models.Model):
    title= models.CharField(max_length=30)

    def __str__(self):
        return self.title

class Post(models.Model):
    title = models.CharField(max_length=100)
    overview = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    comment_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='postImages/')
    categories = models.ManyToManyField(Category)
    featured = models.BooleanField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail',kwargs={
            'id' : self.id
        })