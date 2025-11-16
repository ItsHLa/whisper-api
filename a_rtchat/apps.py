from django.apps import AppConfig


class ARtchatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'a_rtchat'
    
    def ready(self) -> None:
        import a_rtchat.signals
