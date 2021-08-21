from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from dquora.helpers import ajax_required
from dquora.messager.models import Message


class MessagesListView(LoginRequiredMixin, ListView):
    """私信列表页"""
    model = Message
    template_name = 'messager/message_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MessagesListView, self).get_context_data()
        # 获取除当前登录用户外的所有用户，按最近登录时间降序排列
        # get_user_model()获取用户模型，is_active=True当前激活的用户
        context['users_list'] = get_user_model().objects.filter(is_active=True).exclude(
            username=self.request.user).order_by('-last_login')[:10]
        # 最近一次私信互动的用户
        last_conversation = Message.objects.get_most_recent_conversation(self.request.user)
        context['active'] = last_conversation.username
        return context

    def get_queryset(self):
        """最近私信互动的内容"""
        active_user = Message.objects.get_most_recent_conversation(self.request.user)
        return Message.objects.get_conversation(self.request.user, active_user)


class ConversationListView(MessagesListView):
    """与指定用户的私信内容"""

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ConversationListView, self).get_context_data()
        # url.py中设置的username参数，表示指定的用户
        context['active'] = self.kwargs["username"]
        return context

    def get_queryset(self):
        # 获取URL中username参数指定的用户
        active_user = get_object_or_404(get_user_model(),
                                        username=self.kwargs["username"])
        return Message.objects.get_conversation(self.request.user, active_user)


@login_required
@ajax_required
@require_http_methods(['POST'])
def send_message(request):
    """发送消息，AJAX POST 请求"""
    sender = request.user
    recipient_user_name = request.POST['to']
    recipient = get_user_model().objects.get(username=recipient_user_name)
    message = request.POST['message']
    if len(message.strip()) != 0 and sender != recipient:
        msg = Message.objects.create(sender=sender, recipient=recipient, message=message)
        channel_layer = get_channel_layer()  # 获得频道层
        # 数据字典
        payload = {
            'type': 'receive',  # 固定写法，表示使用consumer.py的receive方法
            # 下面为传递的消息数据
            'message': render_to_string('messager/single_message.html', {'message': msg}),
            'sender': sender.username
        }
        # consumer中异步函数变为同步
        # 在频道层内，使用group_send(group所在组-接收者的username, message消息内容)往recipient_user_name组内发送数据payload
        async_to_sync(channel_layer.group_send)(recipient_user_name, payload)
        return render(request, 'messager/single_message.html', {'message': msg})
    return HttpResponse()


@login_required
@ajax_required
@require_http_methods(['GET'])
def receive_message(request):
    """接收消息， AJAX GET 请求"""
    message_id = request.GET['message_id']
    msg = Message.objects.get(pk=message_id)
    return render(request, 'messager/single_message.html', {'message': msg})
