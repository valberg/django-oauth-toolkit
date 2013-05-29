from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _

from .generators import generate_client_secret, generate_client_id
from .validators import validate_uris


class Application(models.Model):
    """
    An Application instance represents a Client on the Authorization server. Usually an Application is created manually
    by client's developers after logging in on an Authorization Server.

    Fields:

    * :attr:`client_id` The client identifier issued to the client during the registration process as \
    described in :rfc:`2.2`
    * :attr:`default_redirect_uri` The URI used for redirection during *Authorization code* workflow when clients do \
    not specify one for their own during the authorization request
    * :attr:`client_type` Client type as described in :rfc:`2.1`
    * :attr:`authorization_grant_type` Authorization flows available to the Application
    * :attr:`client_secret` Confidential secret issued to the client during the registration process as \
    described in :rfc:`2.2`
    * :attr:`name` Friendly name for the Application
    * :attr:`user` ref to a Django user
    """
    CLIENT_CONFIDENTIAL = 'confidential'
    CLIENT_PUBLIC = 'public'
    CLIENT_TYPES = (
        (CLIENT_CONFIDENTIAL, _('Confidential')),
        (CLIENT_PUBLIC, _('Public')),
    )

    GRANT_ALLINONE = 'all-in-one'
    GRANT_AUTHORIZATION_CODE = 'authorization-code'
    GRANT_IMPLICIT = 'implicit'
    GRANT_PASSWORD = 'password'
    GRANT_CLIENT_CREDENTIAL = 'client-credential'
    GRANT_TYPES = (
        (GRANT_ALLINONE, _('All-in-one generic')),
        (GRANT_AUTHORIZATION_CODE, _('Authorization code')),
        (GRANT_IMPLICIT, _('Implicit')),
        (GRANT_PASSWORD, _('Resource owner password-based')),
        (GRANT_CLIENT_CREDENTIAL, _('Client credentials')),
    )

    client_id = models.CharField(max_length=100, unique=True,
                                 default=generate_client_id)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    redirect_uris = models.TextField(help_text=_("Allowed URIs list space separated"), validators=[validate_uris])

    client_type = models.CharField(max_length=32, choices=CLIENT_TYPES)
    authorization_grant_type = models.CharField(max_length=32, choices=GRANT_TYPES)
    client_secret = models.CharField(max_length=255, blank=True, default=generate_client_secret)
    name = models.CharField(max_length=255, blank=True)

    @property
    def default_redirect_uri(self):
        return self.redirect_uris.split().pop(0)

    def redirect_uri_allowed(self, uri):
        uri = uri.rstrip("/")
        return uri in self.redirect_uris.split()

    def __unicode__(self):
        return self.client_id


class Grant(models.Model):
    """

    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    code = models.CharField(max_length=255)  # code comes from oauthlib
    application = models.ForeignKey(Application)
    expires = models.DateTimeField(null=True)  # TODO generate short expire time
    redirect_uri = models.CharField(max_length=255)
    scope = models.TextField(blank=True)

    def is_expired(self):
        return timezone.now() >= self.expires

    def redirect_uri_allowed(self, uri):
        return uri == self.redirect_uri.rstrip("/")

    def __unicode__(self):
        return self.code


class AccessToken(models.Model):
    """

    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    token = models.CharField(max_length=255)  # TODO generate code
    application = models.ForeignKey(Application)
    expires = models.DateTimeField()  # TODO provide a default value based on the settings
    scope = models.TextField(blank=True)

    def is_valid(self, scopes=None):
        """
        Checks if the access token is valid.
        """
        return not self.is_exired() and self.allow_scopes(scopes)

    def is_exired(self):
        return timezone.now() >= self.expires

    def allow_scopes(self, scopes):
        """
        Check if the token allows the provided scopes

        Fields:

        * :attr:`scopes` A list of the scopes to check
        """
        if not scopes:
            return True

        provided_scopes = set(self.scope.split())
        resource_scopes = set(scopes)

        return resource_scopes.issubset(provided_scopes)

    def __unicode__(self):
        return self.token


class RefreshToken(models.Model):
    """

    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    token = models.CharField(max_length=255)  # TODO generate code
    application = models.ForeignKey(Application)
    access_token = models.OneToOneField(AccessToken, related_name='refresh_token')

    def __unicode__(self):
        return self.token