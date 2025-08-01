import importlib

# Ensure the main library modules can be imported.
modules = [
    'pyskoob.client',
    'pyskoob.auth',
    'pyskoob.books',
    'pyskoob.users',
    'pyskoob.profile',
    'pyskoob.http.client',
    'pyskoob.http.httpx',
    'pyskoob.utils.bs4_utils',
    'pyskoob.utils.skoob_parser_utils',
]

for mod in modules:
    importlib.import_module(mod)
