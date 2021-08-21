from django.db import models
from django.conf import settings
import uuid

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from dquora.notifications.views import notification_handler


# Create your models here.


class News(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                             related_name='publisher', verbose_name='用户')
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='thread',
                               verbose_name='自关联')
    content = models.TextField(verbose_name='动态内容')
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_news',
                                   verbose_name='点赞用户')
    reply = models.BooleanField(default=False, verbose_name='是否为评论')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '首页'
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self):
        return self.content

    # 重载save()方法，当有一条动态建立时，WS通知其他用户有新动态了
    # 说得不对，不会自动创建一条Notification实例，Notification字段指明给模型类关联了，
    # 没指定具体的一条数据（ Notification使用GenericForeignKey，所以New新建一条动态时，也会自动新建一条Notification实例）
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(News, self).save()
        if not self.reply:
            # 仅给consumer传入数据用于通知‘notifications’组的其他用户们，不创建一条新Notification实例的
            channel_layer = get_channel_layer()
            payload = {
                'type': 'receive',
                'key': 'additional_news',
                'actor_name': self.user.username
            }
            async_to_sync(channel_layer.group_send)('notifications', payload)

    def switch_like(self, user):
        """点赞或取消赞"""
        # self.liked.all()表示给该条动态点赞的所有用户，而下面的remove()、add()是django关联对象的方法。
        if user in self.liked.all():
            self.liked.remove(user)
        else:
            self.liked.add(user)
            # 新增点赞， 通知楼主（动态发布者）,新建了一条Notification实例
            notification_handler(user, self.user, 'L', self, key='social_update', id_value=str(self.uuid))

    def get_parent(self):
        """返回自关联中的上级记录或本身"""
        # 是评论，有上级记录，返回上级
        if self.parent:
            return self.parent
        else:
            # 返回本身
            return self

    def reply_this(self, user, text):
        """
        回复首页的动态
        :param user: 登录的用户
        :param text: 回复的内容
        :return:
        """
        parent = self.get_parent()
        News.objects.create(
            user=user,
            content=text,
            reply=True,
            parent=parent
        )
        # 新增评论，通知楼主
        notification_handler(user, parent.user, 'R', parent, key='social_update', id_value=str(parent.uuid))

    def get_thread(self):
        """关联到当前记录的所有记录"""
        # 当前记录的上级记录
        parent = self.get_parent()
        # 上级记录(parent)下的子记录(thread)所有
        return parent.thread.all()

    def comment_count(self):
        """评论数"""
        return self.get_thread().count()

    def count_likers(self):
        """点赞数"""
        return self.liked.count()

    def get_likers(self):
        """所有点赞用户"""
        return self.liked.all()
