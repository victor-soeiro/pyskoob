import importlib

modules = [
    'pyskoob.auth',
    'pyskoob.books',
    'pyskoob.users',
    'pyskoob.profile',
    'pyskoob.models.author',
]

for mod in modules:
    importlib.import_module(mod)
