# -*- coding: utf-8 -*-

import os
import distutils.util

def env_bool(env, default):
    if os.environ.get(env):
        return distutils.util.strtobool(os.environ.get(env))
    else:
        return default


def env_str(env, default):
    return os.getenv(env, default)


def env_int(env, default):
    if os.environ.get(env):
        return int(os.environ.get(env))
    else:
        return default

debug = env_bool('DEBUG', True)
#db_host = env_str('DB_HOST', db_host)
#db_username = env_str('DB_USERNAME', db_username)
#db_password = env_str('DB_PASSWORD', db_password)
#db_dbname = env_str('DB_DBNAME', db_dbname)
#db_port = env_int('DB_PORT', db_port)

LANGUAGES = {
    'en': 'English'
}

#Add or remove tested attributes here. Its enough to just list the name (common for both .js and .json file).
tested_attributes = {
    "encoding",
    "headersList",
    "language",
    "userAgent",
    "adBlock",
    "audio",
    "buildID",
    "canvas_blob",
    "canvas",
    "color_depth",
    "device",
    "ECMAarrays",
    "geolocation",
    "IE_add",
    "index_db",
    "IOdevices",
    "jsFonts",
    "lie",
    "mathRoutine",
    "methodsToString",
    "navigator",
    "open_db",
    "performance",
    "referrer",
    "screen",
    "storage",
    "time",
    "timezone",
    "touch",
    "webgl",
    "worker"
}

