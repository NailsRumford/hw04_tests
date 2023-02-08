from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from core.utils import paginator
from django.shortcuts import get_object_or_404, redirect, render


from .forms import PostForm, CommentsForm
from .models import Group, Post, Comment


User = get_user_model()


def index(request):
    """ Возвращает главную страницу с десятью последними постами """
    post_list = Post.objects.select_related('author').all()
    page_obj = paginator(post_list, request)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """ Возращает страницу с постами группы """
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(post_list, request)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj, }

    return render(request, template, context)


def profile(request, username):
    """ Возвращает страничку пользователя с десятью последними постами """
    author = get_object_or_404(User, username=username)
    posts_author = author.posts.all()
    page_obj = paginator(posts_author, request)
    template = 'posts/profile.html'
    context = {'author': author,
               'page_obj': page_obj,
               }
    return render(request, template, context)


def post_detail(request, post_id):
    """ Возвращает страницу поста """
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post = post)
    comment_form = CommentsForm()
    context = {'post': post,
               'comments':comments,
               'comment_form':comment_form,
               }
    return render(request, 'posts/post_detail.html', context)

@login_required
def post_create(request):
    """ Возвращает форму для добавления новой публикации """
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        username = request.user.username
        return redirect('posts:profile', username)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    """ Возвращает форму для редактирования поста с нынешнем содержанием
        Права на редактирование eсть только у автора этого поста
        Остальные пользователи перенаправляться на страницу просмотра поста.
    """
    post = get_object_or_404(Post, id=post_id)
    template_create = 'posts/create_post.html'
    page_detail = 'posts:post_detail'
    if post.author != request.user:
        return redirect(page_detail, post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect(page_detail, post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, template_create, context)

@login_required
def add_comment(request, post_id):
    post =Post.objects.get(id=post_id)
    form = CommentsForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)