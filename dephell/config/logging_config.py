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
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'extras': True,
            '()': 'dephell.logging_helpers.ColoredFormatter',
            'style': '{',
            'colors': True,
            'format': '{levelname:8} {asctime} {message} {extras}',
        },
        'short': {
            'extras': True,
            '()': 'dephell.logging_helpers.ColoredFormatter',
            'style': '{',
            'colors': True,
            'format': '{levelname:8} {message} {extras}',
        },
    },
}
