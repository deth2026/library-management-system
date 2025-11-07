from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.db import transaction, IntegrityError
from .models import Book, UserProfile, Category, Author
from .forms import (
    BookForm, SimpleRegisterForm, UserForm, UserProfileForm,
    CategoryForm, AuthorForm
)
from django.core.paginator import Paginator
from django.db.models import Prefetch


# ================== ROOT / INDEX ==================
def index(request):
    """
    Root URL: redirect to login if not authenticated, else go home
    """
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('login')


# ================== HOME ==================
@login_required
def home(request):
    return render(request, 'home.html')


# ================== LOGIN ==================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Already logged in

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


# ================== REGISTER ==================
def register(request):
    if request.user.is_authenticated:
        return redirect('home')  # Already logged in

    if request.method == 'POST':
        form = SimpleRegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    # Ensure profile exists
                    UserProfile.objects.get_or_create(user=user)
                    login(request, user)
                    messages.success(request, 'Registration successful!')
                    return redirect('home')
            except IntegrityError:
                messages.error(request, 'Registration failed: Integrity error.')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SimpleRegisterForm()
    return render(request, 'register.html', {'form': form})


# ================== LOGOUT ==================
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ================== USER PROFILE HELP ==================

def get_user_profile_or_create(user):
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile


# ================== USERS ==================
@login_required
def user_list(request):
    users_qs = User.objects.order_by('-date_joined').prefetch_related(
        Prefetch('userprofile', queryset=UserProfile.objects.all())
    )
    paginator = Paginator(users_qs, 10)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    return render(request, 'user.html', {'users': users_page})


@login_required
def user_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = get_user_profile_or_create(user)
    return render(request, 'user_profile.html', {'user': user, 'profile': profile})


@login_required
def add_user(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    username = user_form.cleaned_data['username']
                    email = user_form.cleaned_data.get('email', '')
                    password = user_form.cleaned_data.get('password') or User.objects.make_random_password()

                    user = User.objects.create_user(username=username, email=email, password=password)

                    profile = UserProfile.objects.get_or_create(user=user)[0]
                    profile.address = profile_form.cleaned_data.get('address', '') or ''
                    profile.phone_number = profile_form.cleaned_data.get('phone_number', '') or ''
                    profile_image = profile_form.cleaned_data.get('profile_image', None)
                    if profile_image:
                        profile.profile_image = profile_image
                    profile.save()

                    messages.success(request, f'User "{user.username}" created successfully!')
                    return redirect('user_list')
            except IntegrityError:
                messages.error(request, 'A user with that username or email already exists.')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
        else:
            for field, errs in user_form.errors.items():
                for e in errs:
                    messages.error(request, f'User {field}: {e}')
            for field, errs in profile_form.errors.items():
                for e in errs:
                    messages.error(request, f'Profile {field}: {e}')
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'user_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Add User'
    })

@login_required
def user_search(request):
    query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('filter', 'all')
    
    users_qs = User.objects.prefetch_related(
        Prefetch('userprofile', queryset=UserProfile.objects.all())
    ).order_by('-date_joined')
    
    if query:
        if filter_type == 'username':
            users_qs = users_qs.filter(username__icontains=query)
        elif filter_type == 'email':
            users_qs = users_qs.filter(email__icontains=query)
        elif filter_type == 'address':
            users_qs = users_qs.filter(userprofile__address__icontains=query)
        else: 
            users_qs = users_qs.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(userprofile__address__icontains=query) |
                Q(userprofile__phone_number__icontains=query)
            )
    
    paginator = Paginator(users_qs, 10)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    return render(request, 'user.html', {'users': users_page, 'search_query': query})


@login_required
def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = get_user_profile_or_create(user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    user.username = user_form.cleaned_data['username']
                    user.email = user_form.cleaned_data.get('email', '')
                    password = user_form.cleaned_data.get('password', '')
                    if password:
                        user.set_password(password)
                    user.save()
                    profile_form.save()
                    messages.success(request, f'User "{user.username}" updated successfully!')
                    return redirect('user_list')
            except IntegrityError:
                messages.error(request, 'A user with that username or email already exists.')
            except Exception as e:
                messages.error(request, f'Error updating user: {str(e)}')
        else:
            for field, errs in user_form.errors.items():
                for e in errs:
                    messages.error(request, f'User {field}: {e}')
            for field, errs in profile_form.errors.items():
                for e in errs:
                    messages.error(request, f'Profile {field}: {e}')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'user_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': f'Edit {user.username}'
    })


@login_required
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.user == user:
        messages.error(request, "You can't delete the currently logged in user.")
        return redirect('user_list')

    if request.method == 'POST':
        try:
            username = user.username
            user.delete()
            messages.success(request, f'User "{username}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting user: {str(e)}')
        return redirect('user_list')
    return render(request, 'user_confirm_delete.html', {'user': user})


# ================== BOOKS ==================
@login_required
def book_list(request):
    books = Book.objects.select_related('author', 'category').order_by('-created_at')
    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    books_page = paginator.get_page(page_number)
    return render(request, 'book.html', {'books': books_page})


@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book created successfully!')
            return redirect('book_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form, 'title': 'Add Book'})


@login_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form, 'title': f'Edit {book.title}'})


@login_required
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        try:
            title = book.title
            book.delete()
            messages.success(request, f'Book "{title}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting book: {str(e)}')
        return redirect('book_list')
    return render(request, 'book_confirm_delete.html', {'book': book})


from django.shortcuts import render, get_object_or_404
from .models import Book

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book_view.html', {'book': book})


@login_required
def book_search(request):
    query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('filter', 'all')
    
    books = Book.objects.select_related('author', 'category').order_by('-created_at')
    
    if query:
        if filter_type == 'title':
            books = books.filter(title__icontains=query)
        elif filter_type == 'author':
            books = books.filter(author__name__icontains=query)
        elif filter_type == 'category':
            books = books.filter(category__name__icontains=query)
        else:  
            books = books.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(author__name__icontains=query) |
                Q(category__name__icontains=query)
            )
    

    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    books_page = paginator.get_page(page_number)
    return render(request, 'book.html', {'books': books_page, 'search_query': query})



# ================== CATEGORIES ==================
@login_required
def category_list(request):
    categories = Category.objects.order_by('name').all()
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    categories_page = paginator.get_page(page_number)
    return render(request, 'category.html', {'categories': categories_page})



@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form, 'title': f'Edit {category.name}'})


@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        try:
            name = category.name
            category.delete()
            messages.success(request, f'Category "{name}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting category: {str(e)}')
        return redirect('category_list')
    return render(request, 'category_confirm_delete.html', {'category': category})


# ================== SEARCH ==================
@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    
    context = {
        'query': query,
        'search_type': search_type,
        'books': None,
        'users': None,
        'authors': None,
        'categories': None
    }
    
    if query:
        if search_type in ['all', 'books']:
            books = Book.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(author__name__icontains=query) |
                Q(category__name__icontains=query)
            ).select_related('author', 'category').distinct()
            context['books'] = books[:10]  # Limit to 10 results
            
        if search_type in ['all', 'users']:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(userprofile__address__icontains=query)
            ).prefetch_related('userprofile').distinct()
            context['users'] = users[:10]
            
        if search_type in ['all', 'authors']:
            authors = Author.objects.filter(
                Q(name__icontains=query)
            ).prefetch_related('book_set').distinct()
            context['authors'] = authors[:10]
            
        if search_type in ['all', 'categories']:
            categories = Category.objects.filter(
                Q(name__icontains=query)
            ).prefetch_related('book_set').distinct()
            context['categories'] = categories[:10]
    
    return render(request, 'search_results.html', context)

# ================== AUTHORS ==================
@login_required
def author_list(request):
    authors = Author.objects.prefetch_related('book_set').order_by('name').all()
    paginator = Paginator(authors, 10)
    page_number = request.GET.get('page')
    authors_page = paginator.get_page(page_number)
    return render(request, 'author.html', {'authors': authors_page})


@login_required
def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Author created successfully!')
            return redirect('author_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = AuthorForm()
    return render(request, 'author_form.html', {'form': form, 'title': 'Add Author'})


@login_required
def edit_author(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, 'Author updated successfully!')
            return redirect('author_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = AuthorForm(instance=author)
    return render(request, 'author_form.html', {'form': form, 'title': f'Edit {author.name}'})


@login_required
def delete_author(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        try:
            name = author.name
            author.delete()
            messages.success(request, f'Author "{name}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting author: {str(e)}')
        return redirect('author_list')
    return render(request, 'author_confirm_delete.html', {'author': author})

# ================== DASHBOARD ==================

@login_required
def dashboard(request):
    total_users = User.objects.count()
    total_books = Book.objects.count()
    total_authors = Author.objects.count()
    total_categories = Category.objects.count()

    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_books = Book.objects.order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_books': total_books,
        'total_authors': total_authors,
        'total_categories': total_categories,
        'recent_users': recent_users,
        'recent_books': recent_books,
    }
    return render(request, 'dashboard.html', context)
