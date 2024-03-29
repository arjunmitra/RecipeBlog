from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from ckeditor.fields import RichTextField

# Create your models here.
User = get_user_model() # getting user object

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
    overview = models.TextField()# description of recipe
    body = RichTextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='postImages/')
    categories = models.ManyToManyField(Category)
    featured = models.BooleanField()# whether we want to feature post on home page
    favourites = models.ManyToManyField(User,related_name="favourite",default=None,blank=True)
    previous_post = models.ForeignKey('self',related_name='previous',on_delete=models.SET_NULL, blank=True,null=True)
    next_post = models.ForeignKey('self',related_name='next', on_delete=models.SET_NULL,blank=True,null=True)

    def __str__(self):
        return self.title
    # urls for crud operations
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={
            'id': self.id
        })
    def get_update_url(self):
        return reverse('post-update', kwargs={
            'id': self.id
        })
    def get_delete_url(self):
        return reverse('post-delete', kwargs={
            'id': self.id
        })

    @property
    def get_comments(self):
        return self.comments.all().order_by('-timestamp')

    @property
    def view_count(self):
        return PostView.objects.filter(post=self).count()

    @property
    def comment_count(self):
        return Comment.objects.filter(post=self).count()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    post = models.ForeignKey(Post, related_name = "comments",on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class PostView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)