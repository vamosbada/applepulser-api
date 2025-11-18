import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ WebSocket 연결 시 실행 """
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'game_{self.room_id}'

        # 그룹에 참가
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # WebSocket 연결 수락
        await self.accept()

    async def disconnect(self, close_code):
        """ WebSocket 연결 해제 시 실행 """
        # 그룹에서 나가기 
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """ 클라이언트로부터 메시지 받을 때 실행 """
        # json 파싱
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'heart_rate':
            # 심박수 데이터 브로드캐스트
            player_id = data.get('player_id')
            bpm = data.get('bpm')

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_heart_rate',
                    'player_id': player_id,
                    'bpm': bpm,
                }
            )
    async def send_heart_rate(self, event):
        """그룹의 모든 클라이언트에게 심박수 전송"""
        # WebSocket으로 메시지 보내기
        await self.send(text_data=json.dumps({
            'type': 'heart_rate',
            'player_id': event['player_id'],
            'bpm': event['bpm'],
        }
        ))