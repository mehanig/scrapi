import sys
import six


class _Registry(dict):

    ###Fix?!
    _py2_ = six.PY2

    def __init__(self):
        super(_Registry, self).__init__()

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            if self._py2_:
                raise (KeyError('No harvester named "{}"'.format(key)))
            else:
                six.raise_from(KeyError('No harvester named "{}"'.format(key)), BaseException)

    @property
    def beat_schedule(self):
        from celery.schedules import crontab
        return {
            'run_{}'.format(name): {
                'args': [name],
                'schedule': crontab(**inst.run_at),
                'task': 'scrapi.tasks.run_harvester',
            }
            for name, inst
            in self.items()
        }

sys.modules[__name__] = _Registry()
