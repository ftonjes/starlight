import os
import logicmonitor_sdk

requests.packages.urllib3.disable_warnings()


class LogicMonitorSession:

    def __init__(self):
        self.cache = {}
        self._init_session()

    def _init_session(self):

        configuration = logicmonitor_sdk.Configuration()
        configuration.verify_ssl = False
        configuration.company = get_key('LOGICMONITOR_COMPANY_NAME']
        configuration.access_id = get_key('LOGICMONITOR_ACCESS_ID']
        configuration.access_key = get_key('LOGICMONITOR_ACCESS_KEY']

        self.client = logicmonitor_sdk.LMApi(logicmonitor_sdk.ApiClient(configuration))

    def get_all(self: 'Self', method: str, **kwargs) -> list:

        retr = []
        last_found = False
        if 'offset' not in kwargs.keys():
            kwargs['offset'] = 0
        if 'size' not in kwargs.keys():
            kwargs['size'] = 1000
        while not last_found:
            r = getattr(self.client, method)(**kwargs)
            kwargs['offset'] += kwargs['size']
            retr += r.items
            if len(r.items) < kwargs['size']:
                last_found = True
        return retr
