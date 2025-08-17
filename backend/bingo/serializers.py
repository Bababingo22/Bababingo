from rest_framework import serializers
from .models import Transaction, GameRound, User
from django.contrib.auth import get_user_model

class TransactionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    class Meta:
        model = Transaction
        fields = ("id", "timestamp", "type", "type_display", "amount", "running_balance", "note")

class GameRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRound
        fields = ("id", "agent", "created_at", "boards", "active_board_ids", "called_numbers", "total_calls", "status", "game_type", "winning_pattern", "amount")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "is_agent", "operational_credit", "commission_percentage")