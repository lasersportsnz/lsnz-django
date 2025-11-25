import os

import markdown
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.options import re
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView

from .forms import PlayerProfileForm, PostForm, TournamentRegistrationForm
from .models import Event, Grade, Player, Post, Registration, Site, System, Tournament


def load_markdown_content(filename):
    """Load and convert markdown file to HTML"""
    content_path = os.path.join(settings.BASE_DIR, 'lsnz', 'content', filename)

    try:
        with open(content_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
        return markdown.markdown(md_content)
    except FileNotFoundError:
        return '<p>Content not found.</p>'

def index(request):
    context = {}
    return render(request, "lsnz/base.html", context)

class TournamentListView(ListView):
    model = Tournament
    template_name = 'lsnz/tournaments.html'
    context_object_name = 'tournaments'
    ordering = ['-start_date']
    queryset = Tournament.objects.select_related('site', 'system')

class TournamentDetailView(DetailView):
    model = Tournament
    template_name = 'lsnz/tournament_detail.html'
    context_object_name = 'tournament'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tournament = self.get_object()

        # Check if tournament is in the future
        context['is_future_tournament'] = tournament.start_date > timezone.now().date()

        # Check if user is already registered (only if authenticated)
        context['already_registered'] = False
        if self.request.user.is_authenticated:
            # Check if user is registered for any event in this tournament
            user_registrations = Registration.objects.filter(
                event__tournament=tournament,
                player=self.request.user
            ).exists()
            context['already_registered'] = user_registrations

        return context

class SiteListView(ListView):
    model = Site
    template_name = 'lsnz/sites.html'
    context_object_name = 'sites'
    ordering = ['name']

class SiteDetailView(DetailView):
    model = Site
    template_name = 'lsnz/site_detail.html'
    context_object_name = 'site'

class SystemListView(ListView):
    model = System
    template_name = 'lsnz/systems.html'
    context_object_name = 'systems'

class SystemDetailView(DetailView):
    model = System
    template_name = 'lsnz/system_detail.html'
    context_object_name = 'system'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system = self.get_object()
        context['sites'] = Site.objects.filter(system=system).order_by('name')
        context['tournaments'] = Tournament.objects.filter(system=system).select_related('site').order_by('-start_date')
        return context

class PlayerListView(ListView):
    model = Player
    template_name = 'lsnz/players.html'
    context_object_name = 'players'

    def get_queryset(self):
        return Player.objects.all().select_related('grade').order_by('alias')

class PlayerDetailView(DetailView):
    model = Player
    template_name = 'lsnz/player_detail.html'
    context_object_name = 'player'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = self.get_object()
        posts = Post.objects.filter(author=player).order_by('-created_at')
        grades = Grade.objects.all().order_by('points')
        context['posts'] = posts
        context['grades'] = grades
        return context

class PlayerUpdateView(LoginRequiredMixin, UpdateView):
    model = Player
    form_class = PlayerProfileForm
    template_name = 'lsnz/edit_profile.html'
    context_object_name = 'player'

    def get_object(self, queryset=None):
        # Always return the current user's profile
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return f"/players/{self.object.slug}"

class TournamentRegistrationView(LoginRequiredMixin, FormView):
    """View for tournament registration"""
    template_name = 'lsnz/register.html'
    form_class = TournamentRegistrationForm

    def get_tournament(self):
        return get_object_or_404(Tournament, slug=self.kwargs['slug'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tournament'] = self.get_tournament()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tournament'] = self.get_tournament()
        return context

    def form_valid(self, form):
        registrations = form.save()
        if registrations:
            messages.success(
                self.request,
                f'Successfully registered for {len(registrations)} event(s)!'
            )
        else:
            messages.info(self.request, 'No new registrations were created.')
        return super().form_valid(form)

    def get_success_url(self):
        return f"/tournaments/{self.kwargs['slug']}"

class PostListView(ListView):
    model = Post
    template_name = 'lsnz/posts.html'
    context_object_name = 'posts'
    paginate_by = 12
    queryset = Post.objects.select_related('author')

class PostDetailView(DetailView):
    model = Post
    template_name = 'lsnz/post_detail.html'
    context_object_name = 'post'

class PostCreateView(LoginRequiredMixin, CreateView):
    """View for creating new posts"""
    model = Post
    form_class = PostForm
    template_name = 'lsnz/post_editor.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context

    def get_success_url(self):
        return f"/blog/{self.object.slug}"

class PostUpdateView(LoginRequiredMixin, UpdateView):
    """View for editing blog posts"""
    model = Post
    form_class = PostForm
    template_name = 'lsnz/post_editor.html'
    slug_field = 'slug'

    def get_queryset(self):
        # Only allow authors to edit their own posts (or superusers)
        if self.request.user.is_superuser:
            return Post.objects.all()
        return Post.objects.filter(author=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return f"/blog/{self.object.slug}"



def about(request):
    """View for about page"""
    context = {
        'title': 'About Us',
        'text_content': load_markdown_content('about.md')
    }
    return render(request, "lsnz/text_page.html", context)

def privacy(request):
    """View for privacy policy page"""
    context = {
        'title': 'Privacy Policy',
        'text_content': load_markdown_content('privacy.md')
    }
    return render(request, "lsnz/text_page.html", context)

def terms(request):
    """View for terms and conditions page"""
    context = {
        'title': 'Terms and Conditions',
        'text_content': load_markdown_content('terms.md')
    }
    return render(request, "lsnz/text_page.html", context)

def error_403(request, exception):
    """View for 403 error page"""
    return render(request, "errors/403.html", status=403)

def error_404(request, exception):
    """View for 404 error page"""
    return render(request, "errors/404.html", status=404)

def error_500(request):
    """View for 500 error page"""
    return render(request, "errors/500.html", status=500)
