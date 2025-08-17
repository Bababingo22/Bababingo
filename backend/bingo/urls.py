from django.urls import path
from .views import TransactionListView, CreateGameView, GameDetailView, MyTokenObtainPairView, CurrentUserView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("transactions/", TransactionListView.as_view(), name="transactions"),
    path("games/create/", CreateGameView.as_view(), name="create_game"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="game_detail"),
    path("me/", CurrentUserView.as_view(), name="me"),
]