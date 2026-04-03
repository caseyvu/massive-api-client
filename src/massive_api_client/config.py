from dataclasses import dataclass


@dataclass(slots=True)
class MassiveClientConfig:
    massive_api_key: str
    api_base_url: str = "https://api.massive.com"
    timeout_secs: float = 30.0
    rate_limit_sleep_secs: float = 60.0
    rate_limit_max_retries: int = 3