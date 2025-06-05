# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

import datetime
import json

import redis
from django.conf import settings

redis = redis.StrictRedis(host=settings.WORKER_REDIS_HOST)


def _send_item_with_size(key, data, size):
    redis.lpush(key, data)
    redis.ltrim(key, 0, size - 1)


def log_processed_file(worker, recordingid, moduleversion):
    now = datetime.datetime.now()
    key = f"processed-file-{worker}"
    data = {"recording": recordingid, "moduleversion": moduleversion, "date": now.isoformat(), "worker": worker}
    data = json.dumps(data)
    _send_item_with_size(key, data, 5)


def log_module_action(module, user, action):
    """
    Actions could be:
        deletemodule
        deleteversion
    """
    now = datetime.datetime.now()
    key = f"module-action-{module}"
    data = {"date": now.isoformat(), "action": action}
    data = json.dumps(data)
    _send_item_with_size(key, data, 5)


def delete_module_action(module):
    """If a module is deleted, we no longer need all of
    its log messages."""
    key = f"module-action-{module}"
    redis.delete(key)


def get_processed_files(worker):
    key = f"processed-file-{worker}"
    data = redis.lrange(key, 0, -1)
    data = [json.loads(d) for d in data]
    data = sorted(data, key=lambda x: x["date"])
    return data


def get_worker_actions(worker):
    key = f"worker-action-{worker}"
    data = redis.lrange(key, 0, -1)
    data = [json.loads(d) for d in data]
    data = sorted(data, key=lambda x: x["date"])
    return data


def get_module_actions(module):
    key = f"module-action-{module}"
    data = redis.lrange(key, 0, -1)
    data = [json.loads(d) for d in data]
    data = sorted(data, key=lambda x: x["date"])
    return data
