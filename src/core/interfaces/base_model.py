from dataclasses import dataclass


@dataclass
class BaseModel:
    """Base model obj"""

    @classmethod
    def from_json(cls, json_data):
        filtered = {v: json_data[v] for (k, v) in enumerate(json_data) if v in cls.__get_keys()}
        return cls(**filtered)

    @classmethod
    def __get_keys(cls):
        """Return the list of class attributes"""
        return [v for (k, v) in enumerate(cls.__annotations__)]