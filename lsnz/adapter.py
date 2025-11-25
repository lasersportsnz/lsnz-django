from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom allauth adapter to redirect users to their profile after login."""

    def get_login_redirect_url(self, request):
        """
        Redirect to the user's profile page (using their alias as the slug)
        instead of the default /accounts/profile/.
        """
        if request.user.is_authenticated:
            return reverse('lsnz:player_detail', kwargs={'slug': request.user.slug})
        return super().get_login_redirect_url(request)
