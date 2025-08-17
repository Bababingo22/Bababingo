from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Transaction, GameRound, User
from .serializers import TransactionSerializer, GameRoundSerializer, UserSerializer
from rest_framework.decorators import api_view, permission_classes
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["is_agent"] = user.is_agent
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class TransactionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_agent:
            return Response({"detail": "Only agents have transaction histories."}, status=status.HTTP_403_FORBIDDEN)
        qs = Transaction.objects.filter(agent=user).order_by("-timestamp")
        serializer = TransactionSerializer(qs, many=True)
        return Response(serializer.data)

class CreateGameView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_agent:
            return Response({"detail": "Only agents can create games."}, status=status.HTTP_403_FORBIDDEN)
        # Required payload: amount, game_type, winning_pattern
        amount = request.data.get("amount")
        game_type = request.data.get("game_type", "Regular")
        winning_pattern = request.data.get("winning_pattern", "Line")
        if amount is None:
            return Response({"detail": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount = Decimal(amount)
        except:
            return Response({"detail": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)
        # Calculate launch cost (for this implementation, we use amount as the launch cost).
        launch_cost = amount
        if user.operational_credit < launch_cost:
            return Response({"detail": "Insufficient operational credit."}, status=status.HTTP_400_BAD_REQUEST)
        # Deduct
        user.operational_credit = user.operational_credit - launch_cost
        user.save()
        # Create transaction record
        tx = Transaction.objects.create(
            agent=user,
            type="GAME_LAUNCH",
            amount=-launch_cost,
            running_balance=user.operational_credit,
            note=f"Game launch cost for {game_type}"
        )
        # Create GameRound
        game = GameRound.objects.create(
            agent=user,
            game_type=game_type,
            winning_pattern=winning_pattern,
            amount=amount,
            status="PENDING"
        )
        serializer = GameRoundSerializer(game)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class GameDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        game = get_object_or_404(GameRound, pk=pk)
        # ensure agent owns it or is staff
        if request.user != game.agent and not request.user.is_staff:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        serializer = GameRoundSerializer(game)
        return Response(serializer.data)

class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)