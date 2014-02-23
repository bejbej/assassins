from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = 'Assassins'
settings.subtitle = ''
settings.author = 'you'
settings.author_email = 'you@example.com'
settings.keywords = ''
settings.description = ''
settings.layout_theme = 'Default'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = '4a69e872-3c22-4c27-82f3-7effc8fbcf21'
#settings.email_server = 'localhost'
#settings.email_sender = 'you@example.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []
