from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404,redirect,reverse
from .models import Post, Category, Author
from django.db.models import Count, Q
from .forms import CommentForm, PostForm

def get_author(user):
    qs= Author.objects.filter(user=user.id)
    if qs.exists():
        return qs[0]
    return None

def category_search(request):
    query = request.GET.get('category')
    category = Category.objects.filter(title = query)
    queryset = Post.objects.filter(categories = category[0])


    category_count = get_category_count()
    most_recent = Post.objects.order_by("-timestamp")[:3]
    paginator = Paginator(queryset, 4)
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


def search(request):

    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()


    category_count = get_category_count()
    most_recent = Post.objects.order_by("-timestamp")[:3]
    paginator = Paginator(queryset, 4)
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
    queryset = Post.objects.values('categories__title').annotate(Count('categories__title'))
    return queryset

def index(request):
    featured = Post.objects .filter(featured = True)
    latest = Post.objects.order_by('-timestamp')[0:3]
    context = {
        'object_list': featured,
        'latest' : latest
    }
    return render(request,"index.html",context)

def blog(request):
    category_count = get_category_count()
    most_recent = Post.objects.order_by("-timestamp")[:3]
    post_list = Post.objects.all()
    paginator = Paginator(post_list,4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'queryset' : paginated_queryset,
        'most_recent' : most_recent,
        'page_request_var': page_request_var,
        'category_count' : category_count
    }
    return render(request,"blog.html",context)

def post(request,id):
    post = get_object_or_404(Post, id=id)
    most_recent = Post.objects.order_by("-timestamp")[:3]
    category_count = get_category_count()
    form = CommentForm(request.POST  or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect('post-detail', id=id)
    context = {
        'post' : post,
        'most_recent': most_recent,
        'category_count': category_count,
        'form' : form


    }
    return render(request,"post.html",context )

def post_create(request ):
    form = PostForm(request.POST or None, request.FILES or None )
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = get_author(author)
            form.save()
            return redirect(reverse("post-detail",kwargs={
                'id' : form.instance.id
            }))
        else:
            print(form.errors)
    context = {
        'form':form
    }
    return render(request,"post_create.html" , context)

def post_update(request,id):
    pass

def post_delete(request,id):
    pass