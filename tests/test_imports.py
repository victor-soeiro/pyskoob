import importlib

modules = [
    'app.api.routers.books',
    'app.api.routers.profile_actions',
    'app.api.routers.users',
    'app.models.author',
]

for mod in modules:
    importlib.import_module(mod)
