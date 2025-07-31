import importlib

modules = [
    'pyskoob.books',
    'pyskoob.users',
    'pyskoob.profile',
    'pyskoob.auth',
]

for mod in modules:
    importlib.import_module(mod)
