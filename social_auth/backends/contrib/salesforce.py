"""
settings.py should include the following:

    SALESFORCE_CLIENT_ID = '...'
    SALESFORCE_CLIENT_SECRET = '...'

    Optional scope to include:
	api: Allows access to the current, logged-in user's account over the APIs, such as the REST API or Bulk API.
	chatter_api: Allows access to only the Chatter API URLs.
	full: Allows access to all data accessible by the current, logged-in user.
	id: Allows access only to the Identity Service
	refresh_token: Allows a refresh token to be returned if you are eligible to receive one.
	visualforce: Allows access to Visualforce pages
	web: Allows the ability to use the access_token on the web.

	If you do not supply a scope parameter, it will default to: id api refresh_token

    SALESFORCE_AUTH_EXTRA_ARGUEMENTS = {'scope': 'id api refresh_token'}
    SALESFORCE_DISPLAY_PARAM = ''


    More information on scope can be found at:
    http://wiki.developerforce.com/page/Digging_Deeper_into_OAuth_2.0_on_Force.com
"""
from urllib import urlencode

from django.utils import simplejson

from social_auth.backends import BaseOAuth2, OAuthBackend
from social_auth.utils import dsa_urlopen, setting

from oauth2 import Token


SALESFORCE_DOMAIN = 'login.salesforce.com'
SALESFORCE_TEST_DOMAIN = 'test.salesforce.com'

SALESFORCE_TESTING = setting('SALESFORCE_TESTING',False)
SALESFORCE_SERVER = "https://" + (SALESFORCE_TEST_DOMAIN if SALESFORCE_TESTING else SALESFORCE_DOMAIN)

SALESFORCE_AUTHORIZATION_PATH = '/services/oauth2/authorize'
SALESFORCE_ACCESS_TOKEN_PATH = '/services/oauth2/token'


SALESFORCE_AUTHORIZATION_URL = SALESFORCE_SERVER + SALESFORCE_AUTHORIZATION_PATH
SALESFORCE_ACCESS_TOKEN_URL = SALESFORCE_SERVER + SALESFORCE_ACCESS_TOKEN_PATH

class SalesforceBackend(OAuthBackend):
    name = 'salesforce'

    EXTRA_DATA = [
        ('user_id', 'user_id'),
        ('asserted_user', 'asserted_user'),
        ('organization_id','organization_id'),
        ('username','username'),
        ('display_name', 'display_name'),
        ('email', 'email'),
        ('status','status'),
        ('photos','photos'),
        ('urls','urls'),
    ]

    def get_user_id(self, details, response):
        return response['user_id']

    def get_user_details(self, response):
        """Return user details from Salesforce account"""
        username = response['username']
        first_name = response['display_name'].split(' ')[0]
        last_name = response['display_name'].split(' ')[-1]
        email = response['email']
        return {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
        }


class SalesforceAuth(BaseOAuth2):
    """Salesforce OAuth mechanism"""
    AUTHORIZATION_URL = SALESFORCE_AUTHORIZATION_URL
    ACCESS_TOKEN_URL = SALESFORCE_ACCESS_TOKEN_URL
    AUTH_BACKEND = SalesforceBackend
    SETTINGS_KEY_NAME = 'SALESFORCE_CLIENT_ID'
    SETTINGS_SECRET_NAME = 'SALESFORCE_CLIENT_SECRET'
    # REDIRECT_STATE = False
    # STATE_PARAMETER = False

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        response = kwargs.get('response') or {}
	import urllib2
	headers = {'Authorization': 'Bearer ' + access_token}
	req = urllib2.Request(response.get('id'), headers=headers)
        try:
            return simplejson.load(urllib2.urlopen(req))
        except ValueError:
            return None


# Backend definition
BACKENDS = {
    'salesforce': SalesforceAuth,
}
