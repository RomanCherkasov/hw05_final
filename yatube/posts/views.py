from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User
from .forms import PostForm


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  'index.html',
                  {'page': page})


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
    return render(request,
                  'profile.html',
                  {'page': page,
                   'author': author,
                   'count_post': count_post, })


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author__username=username)
    count_post = post_list.count()
    post = post_list.filter(id=post_id)
    return render(request,
                  'post.html',
                  {'author': author,
                   'post': post[0],
                   'count_post': count_post, })


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
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
    form = PostForm(request.POST or None, instance=this_post)
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    context = {'form': form,
               'is_edit': True, }
    return render(request,
                  'create_and_edit_post.html',
                  context=context)
