import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationsConsumer(AsyncWebsocketConsumer):
    """处理通知应用中的WebSocket请求"""

    async def connect(self):
        """建立连接"""
        if self.scope['user'].is_anonymous:
            # 未登录用户，拒绝连接
            await self.close()
        else:
            # 把该用户加入到'notifications'组内，进行监听。即所有用户都监听了'notifications'组，只要一有消息，其他用户都能收到
            await self.channel_layer.group_add('notifications', self.channel_name)
            await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        """从views.py中接受到的数据，accept()进行处理后，再返回给前端"""
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        """断开连接"""
        await self.channel_layer.group_discard('notifications', self.channel_name)
