import markdown
import os
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils.text import slugify
from django.db.models import Q, Value
from django.db.models.functions import Lower, Replace
from django.conf import settings
from .models import Event, Site, Player, Grade, Post

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

def events(request):
    events = Event.objects.all().select_related('site').order_by('-date')
    context = {'events': events}
    return render(request, "lsnz/events.html", context)

def sites(request):
    sites = Site.objects.all().order_by('name')
    context = {'sites': sites}
    return render(request, "lsnz/sites.html", context)

def players(request):
    players = Player.objects.all().select_related('grade').order_by('alias')
    grades = Grade.objects.all().order_by('points')
    context = {'players': players, 'grades': grades}
    return render(request, "lsnz/players.html", context)

def event_detail(request, event_slug):
    """View for individual event details"""
    # Find event by matching slugified name, include site data for template
    event = get_object_or_404(
        Event.objects.select_related('site').annotate(
            slug=Replace(Lower('name'), Value(' '), Value('-'))
        ).filter(slug=event_slug.lower())
    )

    # TODO: Add logic for is_future_event and already_registered
    context = {
        'event': event,
        'is_future_event': False,  # placeholder
        'already_registered': False,  # placeholder
    }
    return render(request, "lsnz/event_detail.html", context)

def site_detail(request, site_slug):
    """View for individual site details"""
    # Find site by matching slugified name using database functions
    site = get_object_or_404(
        Site.objects.annotate(
            slug=Replace(Lower('name'), Value(' '), Value('-'))
        ).filter(slug=site_slug.lower())
    )

    context = {'site': site}
    return render(request, "lsnz/site_detail.html", context)

def player_detail(request, alias):
    """View for individual player details"""
    player = get_object_or_404(Player.objects.select_related('grade'), alias=alias)

    # Get posts by this player
    posts = Post.objects.filter(author=player).order_by('-created_at')

    context = {
        'player': player,
        'posts': posts,
    }
    return render(request, "lsnz/player_detail.html", context)

def event_register(request, event_slug):
    """View for event registration"""
    event = get_object_or_404(
        Event.objects.select_related('site').annotate(
            slug=Replace(Lower('name'), Value(' '), Value('-'))
        ).filter(slug=event_slug.lower())
    )

    if request.method == 'POST':
        # TODO: Implement registration logic
        return HttpResponse(f"Registration for {event.name} submitted (placeholder)")

    context = {'event': event}
    return render(request, "lsnz/register.html", context)

def event_deregister(request, event_slug):
    """View for event deregistration"""
    if request.method == 'POST':
        # TODO: Implement deregistration logic
        return HttpResponse(f"Deregistration from {event_slug} processed (placeholder)")
    return HttpResponse("Method not allowed", status=405)

def blog(request, page=1):
    """View for blog posts with pagination"""
    posts = Post.objects.select_related('author').order_by('-created_at')
    # TODO: Implement proper pagination
    context = {
        'posts': posts,
        'page': page,
        'pages': [1],  # placeholder
        'total_pages': 1,  # placeholder
        'prev_url': None,
        'next_url': None,
        'show_last': False,
    }
    return render(request, "lsnz/posts.html", context)

def post_detail(request, post_slug):
    """View for individual post details"""
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__grade').annotate(
            slug=Replace(Lower('title'), Value(' '), Value('-'))
        ).filter(slug=post_slug.lower())
    )

    context = {
        'post': post,
        'content': post.body,  # TODO: Process markdown or rich text
    }
    return render(request, "lsnz/post_detail.html", context)

def write_post(request):
    """View for creating new posts"""
    # TODO: Implement post creation form
    return HttpResponse("Write post form (placeholder)")

def edit_blog_post(request, post_slug):
    """View for editing blog posts"""
    # TODO: Implement post editing form
    return HttpResponse(f"Edit post {post_slug} (placeholder)")

def edit_profile(request):
    """View for editing user profile"""
    # TODO: Implement profile editing form
    return HttpResponse("Edit profile form (placeholder)")

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
