from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Profile, Blog,Comment,Category
from django.contrib.auth.decorators import login_required
from django.db.models import Count,Q

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        image = request.FILES.get('image')  # profile picture

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)

        profile, created = Profile.objects.get_or_create(user=user)
        if image:
            profile.image = image
            profile.save()

        messages.success(request, "Account created. Please log in.")
        return redirect('loginusr')

    return render(request, 'register.html')

def loginusr(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('loginusr')
    return render(request, 'login.html')

def logoutusr(request):
    logout(request)
    return redirect('loginusr')



def crtblog(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        category = None
        if category_id:
            category = Category.objects.get(id=category_id)

        Blog.objects.create(
            title=title,
            content=content,
            image=image,
            author=request.user,
            category=category
        )
        return redirect('home')

    categories = Category.objects.all()
    return render(request, 'crtblog.html', {'categories': categories})

@login_required(login_url='loginusr')
def home(request):
    if request.User.is_authenticated:
        blogs = Blog.objects.all().order_by('-created_at')
        return render(request, 'home.html', {'blogs': blogs})
    else:
        return redirect(loginusr)



@login_required(login_url='loginusr')
def home(request):
        query = request.GET.get('q')
        filter_type = request.GET.get('filter')  
        category_id = request.GET.get('category')

        blogs = Blog.objects.all()

        if filter_type == 'latest':
            blogs = blogs.order_by('-created_at')

        elif filter_type == 'trending':
            blogs = blogs.annotate(comment_count=Count('comments')).order_by('-comment_count', '-created_at')

        elif category_id:
            blogs = blogs.filter(category_id=category_id).order_by('-created_at')

        else:
            blogs = blogs.order_by('-created_at')  

        if query:
            blogs = blogs.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        categories = Category.objects.all()

        return render(request, 'home.html', {
            'blogs': blogs,
            'categories': categories,
            'active_filter': filter_type,
            'active_category': int(category_id) if category_id else None,
        })



def post_detail(request, id):
    post = get_object_or_404(Blog, id=id)
    return render(request, 'post_detail.html', {'post': post})



def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = Blog.objects.filter(author=user).order_by('-created_at')
    return render(request, 'profile.html', {'user_profile': user, 'posts': posts})



@login_required
def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'profile.html', {'profile_user': user})

@login_required
def edit_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.user != user:
        return redirect('home')

    if request.method == 'POST':
        if 'image' in request.FILES:
            profile = user.profile
            profile.image = request.FILES['image']
            profile.save()
            return redirect('profile', user_id=user.id)

    return render(request, 'edit_profile.html', {'user': user})

@login_required
def remove_profile_image(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user == user:
        user.profile.image.delete(save=True)
    return redirect('profile', user_id=user.id)



@login_required
def edit_post(request, id):
    post = get_object_or_404(Blog, id=id)

    if post.author != request.user:
        return redirect('home')  # Only creator can edit

    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')

        if 'image' in request.FILES:
            post.image = request.FILES['image']

        post.save()
        return redirect('post_detail', id=post.id)

    return render(request, 'edit_post.html', {'post': post})


@login_required
def delete_post(request, id):
    post = get_object_or_404(Blog, id=id)

    if post.author == request.user:
        post.delete()
        return redirect('home')
    else:
        return redirect('home')
    



@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Blog, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, user=request.user, content=content)
    return redirect('post_detail', id=post.id)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user or comment.post.author == request.user:
        comment.delete()
    return redirect('post_detail', id=comment.post.id)
