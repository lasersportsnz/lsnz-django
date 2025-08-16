from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Post, Registration, Event, Player, Site


class PostForm(forms.ModelForm):
    """Form for creating and editing blog posts"""

    class Meta:
        model = Post
        fields = ['title', 'summary', 'body', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'summary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief summary of your post',
                'maxlength': '200'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Write your post content here...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        help_texts = {
            'summary': 'A brief description that will appear in post previews (max 200 characters)',
            'body': 'You can use Markdown formatting in your post content',
            'image': 'Upload a featured image for your post (optional)'
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            # Check for duplicate titles (excluding current instance if editing)
            qs = Post.objects.filter(title__iexact=title)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('A post with this title already exists.')
        return title

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validate file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file size must be less than 5MB.')
        return image


class EventRegistrationForm(forms.ModelForm):
    """Form for registering players to tournament events"""

    class Meta:
        model = Registration
        fields = ['event', 'team']
        widgets = {
            'event': forms.Select(attrs={
                'class': 'form-select'
            }),
            'team': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        # Extract tournament from kwargs if provided
        self.tournament = kwargs.pop('tournament', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter events to only show those for this tournament
        if self.tournament:
            self.fields['event'].queryset = Event.objects.filter(
                tournament=self.tournament
            ).select_related('format')
            self.fields['event'].empty_label = "Select an event"

            # Customize event display
            self.fields['event'].label_from_instance = lambda obj: f"{obj.format.name} - {obj.start_time.strftime('%B %d, %I:%M %p')}"

        # Make team optional for now
        self.fields['team'].required = False
        self.fields['team'].empty_label = "No team (individual entry)"

    def clean_event(self):
        event = self.cleaned_data.get('event')
        if event and self.user:
            # Check if user is already registered for this event
            if Registration.objects.filter(event=event, player=self.user).exists():
                raise ValidationError('You are already registered for this event.')

            # Check if event is in the past
            if event.start_time < timezone.now():
                raise ValidationError('Cannot register for events that have already started.')

        return event

    def save(self, commit=True):
        registration = super().save(commit=False)
        if self.user:
            registration.player = self.user
        if commit:
            registration.save()
        return registration


class TournamentRegistrationForm(forms.Form):
    """Form for registering to multiple events in a tournament"""

    def __init__(self, *args, **kwargs):
        self.tournament = kwargs.pop('tournament', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.tournament:
            # Get all events for this tournament
            events = Event.objects.filter(tournament=self.tournament).select_related('format')

            # Get already registered events for this user
            registered_events = set()
            if self.user and self.user.is_authenticated:
                registered_events = set(
                    Registration.objects.filter(
                        event__tournament=self.tournament,
                        player=self.user
                    ).values_list('event_id', flat=True)
                )

            # Create a checkbox for each event
            for event in events:
                field_name = f'event_{event.id}'
                initial = event.id in registered_events
                disabled = event.start_time < timezone.now() or initial

                self.fields[field_name] = forms.BooleanField(
                    label=f"{event.format.name}",
                    help_text=f"{event.start_time.strftime('%B %d, %Y at %I:%M %p')}",
                    required=False,
                    initial=initial,
                    disabled=disabled,
                    widget=forms.CheckboxInput(attrs={
                        'class': 'form-check-input'
                    })
                )

    def clean(self):
        cleaned_data = super().clean()

        # Check that at least one event is selected
        selected_events = [k for k, v in cleaned_data.items() if k.startswith('event_') and v]
        if not selected_events:
            raise ValidationError('Please select at least one event to register for.')

        return cleaned_data

    def save(self):
        """Create registrations for selected events"""
        if not self.user:
            return []

        registrations = []
        for field_name, selected in self.cleaned_data.items():
            if field_name.startswith('event_') and selected:
                event_id = field_name.split('_')[1]
                try:
                    event = Event.objects.get(id=event_id, tournament=self.tournament)
                    # Check if not already registered
                    if not Registration.objects.filter(event=event, player=self.user).exists():
                        registration = Registration.objects.create(
                            event=event,
                            player=self.user
                        )
                        registrations.append(registration)
                except Event.DoesNotExist:
                    continue

        return registrations


class PlayerProfileForm(forms.ModelForm):
    """Form for editing player profiles"""

    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'alias', 'profile_picture', 'bio', 'home_site']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your last name'
            }),
            'alias': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your gaming alias'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'home_site': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        help_texts = {
            'alias': 'This is how other players will see you',
            'profile_picture': 'Upload a profile picture (max 5MB)',
            'bio': 'A brief description about yourself and your gaming experience',
            'home_site': 'Your primary playing location'
        }

    def clean_alias(self):
        alias = self.cleaned_data.get('alias')
        if alias:
            # Check for duplicate aliases (excluding current instance)
            qs = Player.objects.filter(alias__iexact=alias)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('This alias is already taken. Please choose another.')
        return alias

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            # Validate file size (max 5MB)
            if picture.size > 5 * 1024 * 1024:
                raise ValidationError('Image file size must be less than 5MB.')

            # Validate file type
            if not picture.content_type.startswith('image/'):
                raise ValidationError('File must be an image.')
        return picture

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set up the home_site field with all sites ordered by name
        self.fields['home_site'].queryset = Site.objects.all().order_by('name')
        self.fields['home_site'].empty_label = "Select your home site"
