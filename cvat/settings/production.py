# Copyright (C) 2018 Intel Corporation
#
# SPDX-License-Identifier: MIT

from .base import *

DEBUG = False

INSTALLED_APPS += [
    'mod_wsgi.server',
]

for key in RQ_QUEUES:
    RQ_QUEUES[key]['HOST'] = 'cvat_redis'

CACHEOPS_REDIS['host'] = 'cvat_redis'

# Django-sendfile:
# https://github.com/johnsensible/django-sendfile
SENDFILE_BACKEND = 'sendfile.backends.xsendfile'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': '10.41.0.3',
        'NAME': 'cvat',
        'USER': 'root',
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
    }
}

VOXEL_LABEL_FIRESTORE_COLLECTION = 'labels'
VOXEL_LABEL_BUCKET_NAME = 'voxel-labels'
