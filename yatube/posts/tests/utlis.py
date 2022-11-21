from django.urls import reverse


def reverser(viewname: str):
    def wrapper(kwargs=None):
        return reverse(viewname, kwargs=kwargs)

    return wrapper


URLS = {
    'index': reverser('posts:index'),
    'group_list': reverser('posts:group_list'),
    'post_detail': reverser('posts:post_detail'),
    'post_create': reverser('posts:post_create'),
    'profile': reverser('posts:profile'),
    'post_edit': reverser('posts:post_edit'),
    'add_comment': reverser('posts:add_comment'),
    'follow_index': reverser('posts:follow_index'),
    'profile_follow': reverser('posts:profile_follow'),
    'profile_unfollow': reverser('posts:profile_unfollow'),
}

TEMPLATES = {
    'index': 'posts/index.html',
    'group_list': 'posts/group_list.html',
    'post_detail': 'posts/post_detail.html',
    'post_create': 'posts/create_post.html',
    'profile': 'posts/profile.html',
    'post_edit': 'posts/create_post.html',
    'follow_index': 'posts/follow.html'
}
