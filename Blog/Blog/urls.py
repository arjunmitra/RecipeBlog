"""Blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from post.views import index, blog, post, search, category_search,\
    post_update,post_delete, post_create, favourite_update,favourite_list, PostInfo
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    # home page
    path('', index),

    # refined blog page
    path('blog/', blog, name="post-list"),

    # CRUD operations
    path('create', post_create, name="post-create"),
    path('post/<id>/', post,name="post-detail"),
    path('post/<id>/update/', post_update,name="post-update"),
    path('post/<id>/delete/', post_delete,name="post-delete"),

    # search
    path('search/', search,name="search"),

    # categories
    path('categories', category_search,name="category-search"),

    # Login, Logout, Signup
    path('accounts/', include('allauth.urls')),

    # favourites
    path('fav/<id>/', favourite_update, name="favourite-update"),
    path('favourites/', favourite_list, name="favourite-list"),

    # API
    path('api-auth/', include('rest_framework.urls')),
    # obtain API key
    # To obtain key credentials, you must have a account on the blog
    # make a post request with the following information in the body [form-data]: 'username': your_username, 'password': your_password
    path('api-token-retrieve/', obtain_auth_token, name='api-token-retrieve'),
    # make API request using API key
    # get access to API key using the api-token-retrieve endpoint
    # include following key-value pair in request headers: 'Authorization' : 'Token your_api_key'
    path('api/',PostInfo.as_view(),name='posts-api'),


]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
