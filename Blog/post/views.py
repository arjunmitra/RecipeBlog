from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404,redirect,reverse
from .models import Post, Category, Author, PostView
from django.db.models import Count, Q
from .forms import CommentForm, PostForm
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response


from io import StringIO
from html.parser import HTMLParser

import os

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class PostInfo(APIView):
    def get(self,request, *args, **kwargs):
        # retrieve all posts
        queryset = Post.objects.all()
        # dictionary containing information about each post
        payload = {}
        for i in range(len(queryset)):
            # fields we will share through API
            fields = ['title', 'overview', 'body', 'categories','thumbnail','view_count','comment_count','author','timestamp']
            item = {}
            for field in fields:
                item[field] = ""
            item[fields[0]] = queryset[i].title
            item[fields[1]] = queryset[i].overview
            #removing html tags and whitespaces
            item[fields[2]] =  ' '.join(strip_tags(queryset[i].body).split())
            item[fields[3]] = []
            categories = queryset[i].categories.all()
            for category in categories:
                #categories is a list
                item[fields[3]].append(category.title)
            item[fields[4]] = queryset[i].thumbnail.url
            item[fields[5]] = queryset[i].view_count
            item[fields[6]] = queryset[i].comment_count
            item[fields[7]] = queryset[i].author.user.username
            item[fields[8]] = queryset[i].timestamp
            # inserting into paylaod with key title and value post item
            payload[queryset[i].title] = item

        return Response(payload)

@login_required
def favourite_list(request):
    queryset = Post.objects.filter(favourites=request.user)
    if len(queryset) ==0:
        empty = True
    else:
        empty = False
    context = {'object_list':queryset, "isEmpty":empty}
    return render(request,'favourites.html',context)

@login_required
def favourite_update(request,id):
    post = get_object_or_404(Post,id=id)
    if post.favourites.filter(id=request.user.id).exists():
        post.favourites.remove(request.user)
    else:
        post.favourites.add(request.user)

    return redirect(reverse('post-detail',args=(id,)))

# method to get other object
def get_author(user):
    qs= Author.objects.filter(user=user.id)
    if qs.exists():
        return qs[0]
    return None

# searching by specific category
def category_search(request):
    query = request.GET.get('category') # name of category
    category = Category.objects.filter(title = query)
    queryset = Post.objects.filter(categories = category[0])# filtering by category title

    return general_blog(request,queryset)


def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')# search parameter user passed in
    if query:
        # filtering by checking if query is contained in post title or overview
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct() # not to double count if the query appears in both title and overview
    return general_blog(request,queryset)


def general_blog(request,queryset):
    category_count = get_category_count() # getting all categories and the count of posts within the category
    most_recent = Post.objects.order_by("-timestamp")[:3] # getting latest 3 posts
    paginator = Paginator(queryset, 4) # setting up pagination
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'queryset': paginated_queryset,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count
    }
    return render(request, "blog.html", context)

def get_category_count():
    # mapping from category title to count of posts within that category
    queryset = Post.objects.values('categories__title').annotate(Count('categories__title'))
    return queryset

# home page
def index(request):
    featured = Post.objects .filter(featured = True) # retrieving posts that we want to feature
    latest = Post.objects.order_by('-timestamp')[0:3]
    context = {
        'object_list': featured,
        'latest' : latest
    }
    return render(request,"index.html",context)

# displays all posts
def blog(request):
    queryset = Post.objects.all()
    return general_blog(request,queryset)

# specific post page
def post(request,id):
    post = get_object_or_404(Post, id=id)# retrieving post object
    if post.favourites.filter(id=request.user.id).exists():
        favourite = True
    else:
        favourite = False
    most_recent = Post.objects.order_by("-timestamp")[:3] # getting latest 3 posts
    category_count = get_category_count() # getting category and post counts
    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user,post=post) # if user is authenticated, incrementing view for that post if not viewed before

    form = CommentForm(request.POST  or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()# saving new post
            return redirect('post-detail', id=id)
    context = {
        'post' : post,
        'most_recent': most_recent,
        'category_count': category_count,
        'favourite': favourite,
        'form' : form


    }
    return render(request,"post.html",context )

# create link, only viewable to admin and staff
@login_required
def post_create(request ):
    title="Create"
    form = PostForm(request.POST or None, request.FILES or None )
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = get_author(author) # setting author of post
            form.save() # saving post
            return redirect(reverse("post-detail",kwargs={
                'id' : form.instance.id
            }))
        else:
            print(form.errors)# checking for errors
    context = {
        'title':title,
        'form':form
    }
    return render(request,"post_create.html" , context)
@login_required
def post_update(request,id):
    title = "Update"
    post = get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)# pre loading form with created post
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = get_author(author)
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
        else:
            print(form.errors)
    context = {
        'title'  : title,
        'form': form
    }
    return render(request, "post_create.html", context)

@login_required
def post_delete(request,id):
    post = get_object_or_404(Post,id=id)
    post.delete()# deleting post
    os.remove(settings.MEDIA_ROOT + '/' + str(post.thumbnail)) # deleting img associated with post
    return redirect(reverse("post-list"))

