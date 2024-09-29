from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from blog.forms import PostForm, CommentForm
from blog.models import Subscription, Post, AccessRequest, Tag


# Create your views here.
def home(request):
    tag_slug = request.GET.get('tag')
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        public_posts = Post.objects.filter(is_public=True, tags=tag).order_by('-created_at')
    else:
        public_posts = Post.objects.filter(is_public=True).order_by('-created_at')

    # Если пользователь авторизован
    if request.user.is_authenticated:
        # ID постов, к которым пользователь подал заявку
        requested_posts_ids = AccessRequest.objects.filter(
            requester=request.user
        ).values_list('post_id', flat=True)

        # ID постов с одобренными заявками
        approved_posts_ids = AccessRequest.objects.filter(
            requester=request.user,
            approved=True
        ).values_list('post_id', flat=True)

        # Определяем скрытые посты с одобренными заявками
        hidden_posts_approved = Post.objects.filter(
            is_public=False,
            id__in=approved_posts_ids
        ).filter(
            author__in=Subscription.objects.filter(user=request.user).values_list('followed_user', flat=True)
        ).order_by('-created_at')

        # Определяем скрытые посты, к которым подана заявка, но ещё не одобрена
        hidden_posts_pending = Post.objects.filter(
            is_public=False,
            id__in=requested_posts_ids
        ).exclude(
            id__in=approved_posts_ids  # Исключаем посты, к которым заявка уже одобрена
        ).filter(
            author__in=Subscription.objects.filter(user=request.user).values_list('followed_user', flat=True)
        ).order_by('-created_at')

        # Определяем скрытые посты, к которым пользователь ещё не подавал заявку
        all_hidden_posts_ids = Post.objects.filter(
            is_public=False,
            author__in=Subscription.objects.filter(user=request.user).values_list('followed_user', flat=True)
        ).values_list('id', flat=True)

        hidden_posts_not_requested = Post.objects.filter(
            id__in=all_hidden_posts_ids
        ).exclude(
            id__in=requested_posts_ids
        ).order_by('-created_at')

        return render(request, 'blog/home.html', {
            'tag': tag,
            'tags': Tag.objects.all(),
            'public_posts': public_posts,
            'hidden_posts_pending': hidden_posts_pending,
            'hidden_posts_approved': hidden_posts_approved,
            'hidden_posts_not_requested': hidden_posts_not_requested
        })

    # Если пользователь не авторизован, не показываем скрытые посты
    return render(request, 'blog/home.html', {
        'public_posts': public_posts,
        'tag': tag,
        'tags': Tag.objects.all(),
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(reverse('home'))
    else:
        form = PostForm()
    return render(request, 'blog/create_post.html', {'form': form})


@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    subscriptions = request.user.subscriptions.values_list('followed_user_id', flat=True)
    return render(request, 'blog/user_list.html', {'users': users, 'subscriptions': subscriptions})


@login_required
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'blog/profile.html', {'user': user})


@login_required
def toggle_subscription(request, user_id):
    followed_user = get_object_or_404(User, id=user_id)
    subscription, created = Subscription.objects.get_or_create(
        user=request.user, followed_user=followed_user
    )
    if not created:
        subscription.delete()
    return redirect(reverse('user_list'))


def public_posts(request):
    posts = Post.objects.filter(is_public=True).order_by('-created_at')
    return render(request, 'blog/public_posts.html', {'posts': posts})


@login_required
def request_access(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        AccessRequest.objects.get_or_create(post=post, requester=request.user)
        return redirect(reverse('home'))
    return render(request, 'blog/request_access.html', {'post': post})


@login_required
def manage_requests(request):
    requests = AccessRequest.objects.filter(post__author=request.user)
    return render(request, 'blog/manage_requests.html', {'requests': requests})


@login_required
def approve_request(request, request_id):
    access_request = get_object_or_404(AccessRequest, id=request_id)
    if access_request.post.author == request.user:
        access_request.approved = True
        access_request.save()
    return redirect(reverse('manage_requests'))


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-created_at')
    form = CommentForm()

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.post = post
                comment.save()
                return redirect(reverse('post_detail', kwargs={'post_id': post.id}))
        else:
            return HttpResponseForbidden("Только зарегистрированные пользователи могут оставлять комментарии.")

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'form': form,
        'comments': comments
    })


@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'blog/my_posts.html', {'posts': posts})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect(reverse('post_detail', kwargs={'post_id': post.id}))
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        post.delete()
        return redirect(reverse('my_posts'))

    return render(request, 'blog/confirm_delete.html', {'post': post})
