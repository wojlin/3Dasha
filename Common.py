from dataclasses import dataclass
from typing import Union, List

@dataclass
class BackendResponse:
    success: bool
    info: str
    data: dict


def response_to_json(response: BackendResponse) -> dict:
    return {"success": response.success, "info": response.info, "data": response.data}


class CyclicBuffer:
    def __init__(self, max_capacity: int, default_value):
        self.__max_capacity = max_capacity
        self.__default_value = default_value

        self.__history = [self.__default_value for x in range(self.__max_capacity)]

    def add_value(self, value):
        self.__history.insert(0, value)
        self.__history.pop()

    def get_buffer_content(self) -> List:
        return self.__history
