from dataclasses import dataclass


@dataclass
class ContentSource:
    id: str
    name: str
    display_name: str
    type: str
    fetch_endpoint: str
    description: str
