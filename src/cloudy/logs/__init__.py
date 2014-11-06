from .models import LogEntry


def add_log(text, *args, **kwargs):
    '''
    Shortcut to create a :class:`cloudy.logs.models.LogEntry` object.

    *text* is interpolated *args* and *kwargs* using :meth:`str.format`.

    There are special keyword arguments:

        * user: links this log entry to an
          :class:`django.contrib.auth.models.User` object and creates a nice
          textual representation for it. Note that the user variable is always
          interpolated, even if no user is passed to this function (in which
          case "Anonymous" is interpolated).

        * object: if it defines a :meth:`get_absolute_url` method, it will be
          used as the :attr:`LogEntry.link` atrribute.

    '''
    # Create textual representation of user
    user = kwargs.get('user')
    if user is not None:
        user_repr = '%s <%s>' % (user.username, user.email)
    else:
        user_repr = 'Anonymous'
    kwargs['user'] = user_repr

    # Generate link if an object is passed
    obj = kwargs.get('object')
    if obj is not None and hasattr(obj, 'get_absolute_url'):
        link = obj.get_absolute_url()
    else:
        link = None

    # Format text
    text = text.format(*args, **kwargs)

    # Create log entry
    return LogEntry.objects.create(text=text, user=user, link=link)
