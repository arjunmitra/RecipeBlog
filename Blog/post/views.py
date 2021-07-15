from django.shortcuts import render
from .models import Post
def index(request):
    featured = Post.objects .filter(featured = True)
    latest = Post.objects.order_by('-timestamp')[0:3]
    context = {
        'object_list': featured,
        'latest' : latest
    }
    return render(request,"index.html",context)

def blog(request):
    post_list = Post.objects.all()
    context = {
        'post_list' : post_list
    }
    return render(request,"blog.html",context)

def post(request):
    return render(request,"post.html",{})