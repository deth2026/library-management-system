from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search, name='search'),
    path('', views.index, name='index'),  
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    # Users
    path('users/search/', views.user_search, name='user_search'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:pk>/', views.user_profile, name='user_profile'),
    path('users/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:pk>/', views.delete_user, name='delete_user'),

    # Books
    path('books/search/', views.book_search, name='book_search'),
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/edit/<int:pk>/', views.edit_book, name='edit_book'),
    path('books/delete/<int:pk>/', views.delete_book, name='delete_book'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # Authors
    path('authors/', views.author_list, name='author_list'),
    path('authors/add/', views.add_author, name='add_author'),
    path('authors/edit/<int:pk>/', views.edit_author, name='edit_author'),
    path('authors/delete/<int:pk>/', views.delete_author, name='delete_author'),

    #Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
]
