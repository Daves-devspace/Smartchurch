# scripture/transcription/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from scripture.transcription.controller import TranscriptionController

class TranscriptionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        cmd = data.get("command")
        if cmd == "start_transcription":
            TranscriptionController.start()
        elif cmd == "stop_transcription":
            TranscriptionController.stop()
        else:
            await self.send(json.dumps({"error": "unknown command"}))


# scripture/transcription/consumers.py (continued)

class LiveVerseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "live_verses"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_overlay(self, event):
        await self.send(text_data=json.dumps({
            "chunk":  event["chunk"],
            "verses": event["verses"],
        }))
