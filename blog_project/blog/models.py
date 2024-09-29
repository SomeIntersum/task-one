from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="Слаг")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name="Автор")
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="Слаг")
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_public = models.BooleanField(default=True, verbose_name="Публичный")
    tags = models.ManyToManyField('Tag', blank=True, verbose_name="Теги")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions', verbose_name="Пользователь")
    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers',
                                      verbose_name="Подписан на")

    def __str__(self):
        return f"{self.user.username} подписан на {self.followed_user.username}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="Пост")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    content = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Комментарий от {self.author.username} к посту {self.post.title}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class AccessRequest(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='access_requests', verbose_name="Пост")
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_requests',
                                  verbose_name="Запрашивающий")
    approved = models.BooleanField(default=False, verbose_name="Одобрено")

    def __str__(self):
        return f"Заявка от {self.requester.username} на пост {self.post.title}"

    class Meta:
        verbose_name = "Заявка на доступ"
        verbose_name_plural = "Заявки на доступ"
