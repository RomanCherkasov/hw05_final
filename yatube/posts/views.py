from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  'index.html',
                  {'page': page,
                   'page_number': page_number})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.post_set.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'page': page
    }
    return render(request,
                  'group.html',
                  context=context)


def follow_check(follower, following):
    all_follows = Follow.objects.all()

    for follow in all_follows:
        if str(follow.author) == following:
            return True
    return False


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author__username=username)
    count_post = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    print(request.user)
    check_follow = False
    if str(request.user) != 'AnonymousUser':
        check_follow = follow_check(request.user, username)
    return render(request,
                  'profile.html',
                  {'page': page,
                   'author': author,
                   'profile': author,
                   'count_post': count_post,
                   'following': check_follow, })


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author__username=username)
    count_post = post_list.count()
    form = CommentForm(request.POST or None)
    post = post_list.filter(id=post_id)
    all_comments = post[0].comments.all().order_by('-created')
    return render(request,
                  'post.html',
                  {'author': author,
                   'post': post[0],
                   'count_post': count_post,
                   'form': form,
                   'comments': all_comments,
                   'profile': author,
                   })


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = author
        comment.post = post
        form.save()
    return redirect('post', username, post_id)


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    form = PostForm()
    context = {'form': form,
               'is_edit': False, }
    return render(request,
                  'create_and_edit_post.html',
                  context=context)


@login_required
def post_edit(request, username, post_id):
    this_post = get_object_or_404(Post, pk=post_id, author__username=username)
    if this_post.author != request.user:
        return redirect('post', username, post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=this_post)
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    context = {'form': form,
               'Post': this_post,
               'is_edit': True, }
    return render(request,
                  'create_and_edit_post.html',
                  context=context)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользовательской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    followage = get_list_or_404(Follow, user=request.user)
    print(followage)
    post_list = Post.objects.none()
    for follows in followage:
        post_list |= Post.objects.filter(author__username=str(follows.author))
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    if request.user.username == username:
        return redirect('profile', username)
    all_user_follows = Follow.objects.filter(user=request.user)
    print(all_user_follows)
    username = get_object_or_404(User, username=username)
    follow = Follow(
        user=request.user,
        author=username,
    )
    for each_follow in all_user_follows:
        print(each_follow.author, follow.author)
        if each_follow.author == follow.author:
            return redirect('profile', username)
    follow.save()
    print(request.user.username)
    print(username)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    username = get_object_or_404(User, username=username)
    if str(request.user) != 'AnonymousUser':
        unfollow = get_object_or_404(Follow, user=request.user, author=username)
        unfollow.delete()
    return redirect('profile', username)

