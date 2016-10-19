import string
import time
from collections import namedtuple
from datetime import datetime, timedelta
from itertools import chain


Cookie = namedtuple('Cookie', ['Domain', 'Expires', 'Max_Age',
                               'Secure', 'HttpOnly', 'Path'])

MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
          'Sep', 'Oct', 'Nov', 'Dec')
DAYS = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
DATE_TEMPLATE = '%s, %02d%s%s%s%s %02d:%02d:%02d GMT'

_valid_cookie_chars = (string.ascii_letters +
                       string.digits +
                       "!#$%&'*+-.^_`|~:")
_cookie_quoting_map = {
    ',': '\\054',
    ';': '\\073',
    '"': '\\"',
    '\\': '\\\\',
}
for _i in chain(range(32), range(127, 256)):
    _cookie_quoting_map[_i] = ('\\%03o' % _i).encode('latin1')


def get_date(d, delim='-'):
    """
    Formats dates for HTTP headers, inspired by werkzeug.http._dump_date
    :param d:
    :param delim:
    :return:
    """
    if d is None:
        d = time.gmtime()
    elif isinstance(d, (int, float)):
        d = time.gmtime(d)
    elif isinstance(d, datetime):
        d = d.utctimetuple()

    day = DAYS[d.tm_wday]
    month = MONTHS[d.tm_mon - 1]

    return DATE_TEMPLATE % (day, d.tm_mday, delim, month, delim,
                            str(d.tm_year), d.tm_hour, d.tm_min,
                            d.tm_sec)


class Cookies:
    __slots__ = ('_cookies',)

    def __init__(self, *cookies):
        self._cookies = []

    def set(self, name, value='', secure=False, http_only=True, domain=None,
            path='/', expires=None, max_age=None):
        """
        Create a new cookie to include in the HTTPResponse instance
        :param name:
        :param value:
        :param secure:
        :param http_only:
        :param domain:
        :param path:
        :param expires:
        :param max_age:
        :return:
        """

        def _quote(v):
            buf = []
            valid = True
            for c in v:
                if c not in _valid_cookie_chars:
                    valid = False
                    c = _cookie_quoting_map.get(c, c)
                buf.append(c)
            ret_buffer = ''.join(buf)
            if valid:
                return ret_buffer
            return '"{}"'.format(ret_buffer)


        if path is not None:
            pass  # fix path

        if isinstance(max_age, timedelta):
            max_age = (max_age.days * 60 * 60 * 24) + max_age.seconds

        if expires:
            if not isinstance(expires, str):
                expires = get_date(expires)
        elif max_age is not None:
            expires = get_date(time.time() + max_age)

        buffer = ['{}={}'.format(name, _quote(value))]

        all_properties = (
            ('Domain', domain, True),
            ('Expires', expires, False),
            ('Max-Age', max_age, False),
            ('Secure', secure, None),
            ('HttpOnly', http_only, None),
            ('Path', path, False)
        )

        for key, val, always in all_properties:
            # mark cookie with key, no value
            if always is None:
                if val:
                    buffer.append(key)
                continue

            # key has no value, skip it good
            if val is None:
                continue

            if always:
                val = _quote(val)

            buffer.append('{}={}'.format(key, val))

        return '; '.join(buffer)



print(get_date(None))
print(get_date(1))
print(get_date(datetime.now()))

c = Cookies()
print(c.set('my name', 'is this value', max_age=60))