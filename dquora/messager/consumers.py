import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MessagesConsumer(AsyncWebsocketConsumer):
    """处理私信应用中Websocket 请求"""

    async def connect(self):
        if self.scope['user'].is_anonymous:
            # 未登录的用户拒绝连接
            await self.close()
        else:
            # 加入聊天组(组名，频道名), self.channel_name自动生成频道，也可自定义
            await self.channel_layer.group_add(self.scope['user'].username, self.channel_name)
            await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        """接受私信"""
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        """离开聊天组"""
        await self.channel_layer.group_discard(self.scope['user'].username, self.channel_name)
