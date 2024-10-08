from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User

from .forms import RegisterForm, PostForm
from .models import Post

# Create your views here.
@login_required(login_url="/login")
def home(request):
    posts = Post.objects.all()

    if request.method == "POST":
        method = request.POST.get("_method").lower()
        if method == "delete":
            post_id = request.POST.get("post-id")
            user_id = request.POST.get("user-id")

            if post_id:
                post = Post.objects.filter(id=post_id).first()
                if post and (post.author == request.user or request.user.has_perm("main.delete_post")):
                    post.delete()
            elif user_id:
                user = User.objects.filter(id=user_id).first()
                if user and request.user.is_staff:
                    try:
                        group = Group.objects.get(name="Default")
                        group.user_set.remove(user)
                    except:
                        pass

                    try:
                        group = Group.objects.get(name="mod")
                        group.user_set.remove(user)
                    except:
                        pass

    return render(request, 'main/home.html', {"posts": posts})

@permission_required("main.add_post", login_url="/login", raise_exception=True)
@login_required(login_url="/login")
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("/home")
    else:
        form = PostForm()
    
    return render(request, 'main/create_post.html', {"form": form})

def logout_view(request):
    logout(request)
    return redirect('/login')

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})