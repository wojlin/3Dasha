from dataclasses import dataclass


@dataclass
class BackendResponse:
    success: bool
    info: str
    data: dict


def response_to_json(response: BackendResponse) -> dict:
    return {"success": response.success, "info": response.info, "data": response.data}
