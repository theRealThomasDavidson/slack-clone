from typing import Generic, TypeVar, List, Optional
import uuid

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self):
        self._items: List[T] = []

    def add(self, item: T) -> T:
        self._items.append(item)
        return item

    def get_all(self) -> List[T]:
        return self._items

    def clear(self):
        self._items = []

    def delete(self, id: str) -> bool:
        item = next((item for item in self._items if getattr(item, 'id', None) == id), None)
        if item:
            self._items.remove(item)
            return True
        return False
    