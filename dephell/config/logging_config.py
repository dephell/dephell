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
        'level': 'DEBUG',
        'propagate': False,
    },
    'loggers': {
        'dephell': {
            'handlers': ['stderr', 'stdout'],
            'disabled': False,
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'handlers': {
        'stderr': {
            'stream': 'ext://sys.stderr',
            'level': 'WARNING',  # write to stderr only WARNING and higher
            'formatter': 'simple',
            'class': 'logging.StreamHandler',
        },
        'stdout': {
            'stream': 'ext://sys.stdout',
            'filters': ['level'],  # write to stdout only DEBUG and INFO
            'level': 'DEBUG',
            'formatter': 'simple',
            'class': 'logging.StreamHandler',
        },
    },
    'formatters': {
        'simple': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'extras': True,
            '()': 'dephell.logging_helpers.ColoredFormatter',
            'style': '{',
            'colors': True,
            'format': '{levelname:8} {asctime} {message} {extras}',
        },
    },
}
