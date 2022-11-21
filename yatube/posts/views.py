from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow, POSTS_PER_PAGE
from .forms import PostForm, CommentForm

CACHE_TIMEOUT = 20 * 60


@cache_page(CACHE_TIMEOUT, key_prefix='index_page')
def index(request: HttpRequest) -> HttpResponse:
    """
    View for index page.
    """
    posts = Post.objects.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(
        request.GET.get('page')
    )
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


@cache_page(CACHE_TIMEOUT, key_prefix='group_page')
def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """
    View for group pages. Posts related to a specific group are here.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(
        request.GET.get('page')
    )
    context = {
        'title': f'Записи сообщества {group.title}',
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)

    show_follow, following = False, False
    if (request.user == user) or (not request.user.is_authenticated):
        show_follow = True
    else:
        following = Follow.objects.filter(
            user__follower__user=request.user
        ).exists()

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(
        request.GET.get('page'),
    )
    context = {
        'author': user,
        'full_name': f'{user.first_name} {user.last_name}',
        'posts_count': posts.count(),
        'page_obj': page_obj,
        'show_follow': show_follow,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(
        author=post.author
    ).count()
    pretext = post.text if len(post.text) <= 30 else post.text[:30]
    context = {
        'pretext': pretext,
        'post': post,
        'posts_count': posts_count,
        'form': CommentForm(request.POST or None),
        'comments': post.comments.all(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    post_form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    context = {
        'title': 'Добавить запись',
        'submit': 'Добавить',
        'form': post_form
    }

    if not post_form.is_valid():
        return render(request, 'posts/create_post.html', context)

    model_instance = post_form.save(commit=False)
    model_instance.author = request.user
    model_instance.save()

    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    if post.author.pk != request.user.pk:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'title': 'Изменить запись',
        'submit': 'Сохранить',
        'form': form
    }

    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)

    form = PostForm(request.POST, instance=post)
    form.save()

    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)

    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    return render(request, 'posts/follow.html', {'page_obj': page_obj})


@login_required
def profile_follow(request, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
