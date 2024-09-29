from django.contrib import admin
from blog.models import Post, Tag, Comment, Subscription, AccessRequest


# Регистрация модели Post
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_public')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'content')
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    prepopulated_fields = {'slug': ('title',)}


# Регистрация модели Tag
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


# Регистрация модели Subscription
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'followed_user')
    search_fields = ('user__username', 'followed_user__username')


# Регистрация модели Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('content', 'author__username')
    raw_id_fields = ('post', 'author')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


# Регистрация модели AccessRequest
@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ('post', 'requester', 'approved')
    list_filter = ('approved',)
    search_fields = ('post__title', 'requester__username')
