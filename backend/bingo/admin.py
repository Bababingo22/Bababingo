from django.contrib import admin
from .models import User, Transaction, GameRound
from django.utils import timezone
from decimal import Decimal

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "is_agent", "operational_credit", "commission_percentage", "is_staff", "is_superuser")
    list_filter = ("is_agent", "is_staff", "is_superuser")
    readonly_fields = ("last_login", "date_joined")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Agent info", {"fields": ("is_agent", "operational_credit", "commission_percentage")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    def save_model(self, request, obj, form, change):
        # If editing existing agent and operational_credit changed manually in admin, make Transaction record
        if change:
            old_obj = User.objects.get(pk=obj.pk)
            old_balance = old_obj.operational_credit
            new_balance = obj.operational_credit
            diff = (new_balance - old_balance)
            if diff != 0:
                # create Transaction record
                from .models import Transaction
                Transaction.objects.create(
                    agent=obj,
                    timestamp=timezone.now(),
                    type="MANUAL",
                    amount=diff,
                    running_balance=new_balance,
                    note=f"Manual adjustment by admin {request.user.username}"
                )
        super().save_model(request, obj, form, change)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("agent", "timestamp", "type", "amount", "running_balance")
    list_filter = ("type", "timestamp")
    search_fields = ("agent__username",)

@admin.register(GameRound)
class GameRoundAdmin(admin.ModelAdmin):
    list_display = ("id", "agent", "created_at", "status", "game_type", "total_calls")
    readonly_fields = ("boards", "active_board_ids", "called_numbers")