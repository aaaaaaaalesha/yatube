from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow, POSTS_PER_PAGE
from .forms import PostForm, CommentForm

CACHE_TIMEOUT = 20 * 60
PRETEXT_LENGTH = 30


@cache_page(CACHE_TIMEOUT, key_prefix='index_page')
def index(request: HttpRequest) -> HttpResponse:
    """
    View for index page.
    """
    posts = Post.objects.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """
    View for group pages. Posts related to a specific group are here.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'title': f'Записи сообщества {group.title}',
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    is_follow_visible = (request.user.is_authenticated
                         and request.user != author)
    following = (is_follow_visible
                 and Follow.objects.filter(user=request.user,
                                           author=author).exists())
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'), )
    context = {
        'author': author,
        'full_name': f'{author.first_name} {author.last_name}',
        'posts_count': posts.count(),
        'page_obj': page_obj,
        'following': following,
        'is_follow_visible': is_follow_visible,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(
        author=post.author
    ).count()
    context = {
        'pretext': post.text[:PRETEXT_LENGTH],
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

    post_instance = post_form.save(commit=False)
    post_instance.author = request.user
    post_instance.save()

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
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'posts/follow.html', {'page_obj': page_obj})


@login_required
def profile_follow(request, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    is_followed = Follow.objects.filter(
        user=request.user, author=author
    ).exists()
    if request.user != author and not is_followed:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
