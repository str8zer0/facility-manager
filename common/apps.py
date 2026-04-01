from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = 'common'

    def ready(self):
        import facilities.menu
        import assets.menu
        import maintenance.menu
        import inventory.menu
