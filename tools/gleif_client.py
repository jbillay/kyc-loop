import time
import requests
import config

class GleifError(Exception):
    pass

class GleifClient:
    def __init__(self):
        self.calls = 0

    def get(self, path, **params):
        for attend in range(config.GLEIF_MAX_RETRIES):
            if self.calls >= config.GLEIF_MAX_CALLS:
                raise GleifError(f"GLEIF call budget ({config.GLEIF_MAX_CALLS}) exceeded")
            self.calls += 1
            try:
                r = requests.get(f"{config.GLEIF_API_URL}{path}", params=params, timeout=15)
            except requests.RequestException as e:
                raise GleifError(f"GLEIF unreachable: {e}") from e
            if r.status_code == 429:
                if self.calls < config.GLEIF_MAX_CALLS and attend < (config.GLEIF_MAX_RETRIES - 1):
                    time.sleep(10)
            else:
                try:
                    return_content = r.status_code, r.json()
                except ValueError:
                    return_content = r.status_code, None
                break
        else:
            raise GleifError(f"GLEIF call retries ({config.GLEIF_MAX_RETRIES}) exceeded")
        return return_content