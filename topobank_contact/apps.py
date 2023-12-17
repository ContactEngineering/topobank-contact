from importlib.metadata import version

from topobank.plugins import PluginConfig

__version__ = version("topobank-contact")


class ContactPluginConfig(PluginConfig):
    default = True
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'topobank_contact'
    verbose_name = "Contact Analysis"

    class TopobankPluginMeta:
        name = "Contact Analysis"
        version = __version__
        description = """
        Provides the following statistical analysis functions:
        - Contact mechanics

        """
        logo = "topobank_contact/static/images/ce_logo.svg"
        restricted = True  # User needs permission to access

    def ready(self):
        # make sure the functions are registered now

        # noinspection PyUnresolvedReferences
        import topobank_contact.functions
        # noinspection PyUnresolvedReferences
        import topobank_contact.views
        # noinspection PyUnresolvedReferences
        import topobank_contact.downloads
