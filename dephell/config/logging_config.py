LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'level': {
            'high': 'INFO',
            '()': 'dephell.logging_helpers.LevelFilter',
        },
    },
    'root': {
        'handlers': ['stderr', 'stdout'],
        'disabled': False,
        'level': 'WARNING',
        'propagate': False,
    },
    'loggers': {
        'dephell': {
            'handlers': ['stderr', 'stdout'],
            'disabled': False,
            'level': None,  # defined via config
            'propagate': False,
        },
    },
    'handlers': {
        'stderr': {
            'stream': 'ext://sys.stderr',
            'level': 'WARNING',  # write to stderr only WARNING and higher
            'formatter': 'short',
            'class': 'logging.StreamHandler',
        },
        'stdout': {
            'stream': 'ext://sys.stdout',
            'filters': ['level'],  # write to stdout only DEBUG and INFO
            'level': 'DEBUG',
            'formatter': 'short',
            'class': 'logging.StreamHandler',
        },
    },
    'formatters': {
        'full': {
            '()': 'dephell.logging_helpers.ColoredFormatter',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '{levelname:8} {asctime} {message} {extras}',
            'style': '{',

            'colors': True,
            'extras': True,
            'traceback': False,
        },
        'short': {
            '()': 'dephell.logging_helpers.ColoredFormatter',
            'format': '{levelname:8} {message} {extras}',
            'style': '{',

            'colors': True,
            'extras': True,
            'traceback': False,
        },
    },
}
