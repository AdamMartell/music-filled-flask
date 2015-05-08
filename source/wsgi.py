from playlist import Application

def app_factory(global_config, **local_config):
    return Application.wsgi_app
