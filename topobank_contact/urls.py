from django.urls import path

from .functions import APP_NAME, VIZ_CONTACT_MECHANICS
from .views import contact_mechanics_card_view

# App name determines the internal name space, e.g. example can be references
# as 'contact:example'
app_name = APP_NAME
urlprefix = 'plugins/contact/'
urlpatterns = [
    # GET
    # * Triggers analyses if not yet running
    # * Return state of analyses
    # * Return plot configuration for finished analyses
    # This is a post request because the request parameters are complex.
    path(
        f'card/{VIZ_CONTACT_MECHANICS}/<int:function_id>',
        view=contact_mechanics_card_view,
        name=f'card-{VIZ_CONTACT_MECHANICS}'
    ),
]
