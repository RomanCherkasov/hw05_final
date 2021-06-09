from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def _get_posts(request, filter_: dict):
    post_list = Post.objects.filter(**filter_).select_related(
        'author',
        'group'
    ).all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page


def _read_author(username):
    author = get_object_or_404(User, username=username)
    post_count = Post.objects.filter(author=author).count()
    follow_count = Follow.objects.filter(
        author=author
    ).count()
    self_follow_count = Follow.objects.filter(
        user=author
    ).count()
    return author, post_count, follow_count, self_follow_count


def _read_post(request, post_id):
    post = Post.objects.filter(id=post_id).select_related(
        'author',
        'group'
    ).prefetch_related('comments').last()
    author, count_post, follow_count, self_follow_count = _read_author(post.author.username)
    form = CommentForm(request.POST or None)
    all_comments = post.comments.select_related('author').all().order_by('-created')
    return {
        'author': author,
        'post': post,
        'count_post': count_post,
        'form': form,
        'comments': all_comments,
        'profile': author,
        'follow_count': follow_count,
        'self_follow_count': self_follow_count,
    }


def index(request):
    page = _get_posts(request, {})
    return render(request,
                  'index.html',
                  {'page': page,
                   'page_number': page.number})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page = _get_posts(request, {'group': group})
    return render(request,
                  'group.html',
                  {
                      'group': group,
                      'page': page
                  })


def profile(request, username):
    author, count_post, follow_count, self_follow_count = _read_author(username)
    page = _get_posts(request, {'author': author})
    check_follow = False
    if request.user.is_authenticated:
        check_follow = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
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
    context = _read_post(request, post_id)
    return render(request,
                  'post.html',
                  context)


@login_required
def add_comment(request, username, post_id):
    context = _read_post(request, post_id)
    if context['form'].is_valid():
        comment = context['form'].save(commit=False)
        comment.author = request.user
        comment.post = context['post']
        context['form'].save()
        return redirect('post', username, post_id)
    return render(request,
                  'post.html',
                  context)


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
    return render(request,
                  'create_and_edit_post.html',
                  {'form': form,
                   'is_edit': False, })


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
    return render(request,
                  'create_and_edit_post.html',
                  {'form': form,
                   'Post': this_post,
                   'is_edit': True, })


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
    page = _get_posts(request, {'author__following__user': request.user})
    return render(request, 'follow.html', {'page': page,
                                           'page_number': page.number,})


@login_required
def profile_follow(request, username):
    if request.user.username == username:
        return redirect('profile', username)
    user = get_object_or_404(User, username=username)
    check_follow = Follow.objects.filter(
        user=request.user, author=user
    ).exists()
    if not check_follow:
        follow = Follow(
            user=request.user,
            author=user,
        )
        follow.save()
    return redirect('profile', user.username)


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    unfollow = get_object_or_404(Follow, user=request.user, author=user)
    unfollow.delete()
    return redirect('profile', user.username)
