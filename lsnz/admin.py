from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import Grade, Player, Post, System, Site, Tournament, Settings, Event, Team, Registration, Pass

admin.site.site_title = 'LSNZ'
admin.site.site_header = 'LSNZ administration'

class PlayerAdmin(UserAdmin):
    # The fields to be used in displaying the User model in admin
    list_display = ('email', 'alias', 'first_name', 'last_name', 'grade', 'is_staff', 'playing_since')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'grade', 'home_site', 'date_joined')

    # The fieldsets to be used when displaying the user in admin
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'alias', 'bio', 'profile_picture')}),
        (_('Game info'), {'fields': ('grade', 'home_site', 'playing_since')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # The fieldsets to be used when creating a user in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'alias', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    search_fields = ('email', 'alias', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    # Make playing_since read-only since it's auto_now_add
    readonly_fields = ('playing_since', 'date_joined', 'last_login')

class EventInline(admin.TabularInline):
    model = Event
    extra = 1
    fields = ('start_time', 'end_time', 'format', 'points_cap', 'settings')

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'site', 'start_date', 'end_date', 'system')
    list_filter = ('site', 'system', 'start_date')
    search_fields = ('name', 'site__name')
    inlines = [EventInline]

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('player', 'event', 'team')
    list_filter = ('player', 'event')

admin.site.register(Grade)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Post)
admin.site.register(System)
admin.site.register(Site)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Settings)
admin.site.register(Event)
admin.site.register(Team)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(Pass)
