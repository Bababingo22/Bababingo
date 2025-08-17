import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import GameRound
from asgiref.sync import sync_to_async
import random
import asyncio

class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.group_name = f"game_{self.game_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        action = content.get("action")
        if action == "start":
            # Start broadcasting numbers
            await self.start_game()
        elif action == "call_next":
            await self.call_number()

    @sync_to_async
    def get_game(self):
        return GameRound.objects.get(pk=self.game_id)

    @sync_to_async
    def save_called(self, game, number):
        game.called_numbers.append(number)
        game.total_calls = len(game.called_numbers)
        game.save()

    async def start_game(self):
        game = await self.get_game()
        # build sequence of numbers 1..75 shuffled
        seq = list(range(1, 76))
        random.shuffle(seq)
        # persist sequence in-game called_numbers will be filled progressively
        await self.channel_layer.group_send(self.group_name, {
            "type": "game.message",
            "message": {"action": "sequence_set", "sequence": seq}
        })
        # optionally mark ACTIVE
        await sync_to_async(self.set_active)(game)

    def set_active(self, game):
        game.status = "ACTIVE"
        game.save()

    async def call_number(self):
        # get current game and next uncalled number
        game = await self.get_game()
        sequence = [n for n in range(1,76) if n not in game.called_numbers]
        if not sequence:
            # ended
            await self.channel_layer.group_send(self.group_name, {
                "type": "game.message",
                "message": {"action": "ended"}
            })
            return
        num = random.choice(sequence)
        await self.save_called(game, num)
        # determine next number (peek)
        remaining = [n for n in range(1,76) if n not in game.called_numbers]
        next_number = remaining[0] if remaining else None
        await self.channel_layer.group_send(self.group_name, {
            "type": "game.message",
            "message": {"action": "call_number", "number": num, "next_number": next_number}
        })

    async def game_message(self, event):
        await self.send_json(event["message"])