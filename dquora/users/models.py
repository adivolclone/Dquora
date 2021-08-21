from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for dquora."""

    #: First and last name do not cover name patterns around the globe
    nickname = models.CharField(verbose_name='昵称', null=True, blank=True, max_length=255)
    job_title = models.CharField(verbose_name='职称', max_length=50, null=True, blank=True)
    introduction = models.TextField(verbose_name='简介', null=True, blank=True)
    picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, verbose_name='头像')
    location = models.CharField(verbose_name='城市', max_length=50, null=True, blank=True)
    personal_url = models.URLField(verbose_name='个人链接', max_length=255, null=True, blank=True)
    weibo = models.URLField(verbose_name='微博链接', max_length=255, null=True, blank=True)
    zhihu = models.URLField(verbose_name='知乎链接', max_length=255, null=True, blank=True)
    github = models.URLField(verbose_name='GitHub链接', max_length=255, null=True, blank=True)
    linkedin = models.URLField(verbose_name='Link链接', max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def get_profile_name(self):
        if self.nickname:
            return self.nickname
        return self.username
