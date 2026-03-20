from django.apps import AppConfig


class TopobankContactAppConfig(AppConfig):
    default = True
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'topobank_contact'
    verbose_name = "Contact Analysis"

    def ready(self):
        # make sure the functions are registered now
        import topobank_contact.views  # noqa: F401
        import topobank_contact.workflows  # noqa: F401
