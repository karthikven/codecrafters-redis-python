from typing import Dict, Any, Tuple

class Store:
    def __init__(self):
        self._data: Dict[str, Any] = {}
    def get(self, key: str) -> Any:
        return self._data.get(key)
    def set(self, key: str, value: Any) -> 'Store':
        new_data = self._data.copy()
        new_data[key] = value
        new_store = Store()
        new_store._data = new_data
        return new_store