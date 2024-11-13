from enum import Enum
import json
from datetime import datetime
from uuid import UUID


class SortingByCreationTime(Enum):
    DESC = 'In descending order of the creation time'
    ASC = 'In ascending order of the creation time'  # от раннего к старому

    @property
    def value_for_sort_method(self):
        if self.name == 'DESC':
            return '-created_at'
        return '+created_at'


class UUIDDatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        elif isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S %z")
        return json.JSONEncoder.default(self, obj)
