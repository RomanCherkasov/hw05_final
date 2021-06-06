from django.shortcuts import render, get_object_or_404, redirect
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


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author__username=username)
    count_post = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    check_follow = False
    if request.user.is_authenticated:
        check_follow = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    follow_count = Follow.objects.filter(
        author=author
    ).count()
    self_follow_count = Follow.objects.filter(
        user=author
    ).count()
    return render(request,
                  'profile.html',
                  {'page': page,
                   'author': author,
                   'profile': author,
                   'count_post': count_post,
                   'following': check_follow,
                   'follow_count': follow_count,
                   'self_follow_count': self_follow_count, })


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author__username=username)
    count_post = post_list.count()
    form = CommentForm(request.POST or None)
    post = post_list.filter(id=post_id)
    all_comments = post[0].comments.all().order_by('-created')
    follow_count = Follow.objects.filter(
        author=author
    ).count()
    self_follow_count = Follow.objects.filter(
        user=author
    ).count()
    return render(request,
                  'post.html',
                  {'author': author,
                   'post': post[0],
                   'count_post': count_post,
                   'form': form,
                   'comments': all_comments,
                   'profile': author,
                   'follow_count': follow_count,
                   'self_follow_count': self_follow_count,
                   })


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, pk=post_id)
    form = CommentForm(request.POST or None)
    all_comments = post.comments.all().order_by('-created')
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = author
        comment.post = post
        form.save()
        return redirect('post', username, post_id)
    return render(request,
                  'post.html',
                  {'author': author,
                   'post': post,
                   'count_post': 1,
                   'form': form,
                   'comments': all_comments,
                   'profile': author, })


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
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=this_post)
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
    return render(
        request,
        "misc/404.html",
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    if request.user.username == username:
        return redirect('profile', username)
    username = get_object_or_404(User, username=username)
    check_follow = Follow.objects.filter(
        user=request.user, author=username
    ).exists()
    if not check_follow:
        follow = Follow(
            user=request.user,
            author=username,
        )
        follow.save()
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    username = get_object_or_404(User, username=username)
    unfollow = get_object_or_404(Follow, user=request.user,
                                 author=username)
    unfollow.delete()
    return redirect('profile', username)
