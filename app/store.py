from typing import Dict, Any, Optional, Tuple
import time

class Store:
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._key_expiration: Dict[str, int] = {}
    def get(self, key: str) -> Any:
        if key in self._key_expiration:
            curr_time = int(time.time()*1000)
            expiration = self._key_expiration[key]
            if curr_time > expiration:
                return None
        return self._data.get(key)
    def set(self, key: str, value: Any, expiration: Optional[int]) -> 'Store':
        new_data = self._data.copy()
        new_expiration = self._key_expiration.copy()
        new_data[key] = value
        new_store = Store()
        new_store._data = new_data
        new_store._key_expiration = new_expiration
        if expiration:
            curr_time = int(time.time() * 1000)
            key_expiration_time = curr_time + expiration
            new_store._key_expiration[key] = key_expiration_time
        return new_store