response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
(T('Current'),URL('default','current')==URL(),URL('default','current'),[]),
(T('Join'),URL('default','join')==URL(),URL('default','join'),[]),
(T('Create'),URL('default','create')==URL(),URL('default','create'),[]),
]