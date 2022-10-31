from typing import Any, Dict, Union

from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation


class Client:
    """A client for requesting data from dbt's Metadata API and parsing it into objects"""

    def __init__(  # noqa: D
        self, api_token: str, dbt_metadata_api_url: str = "https://metadata.cloud.getdbt.com/graphql"
    ) -> None:
        headers = {"Authorization": f"token {api_token}"}
        self.endpoint = HTTPEndpoint(url=dbt_metadata_api_url, base_headers=headers)

    def query_operation(self, operation: Operation) -> Union[Any, Dict[str, Any]]:  # type: ignore[misc]
        """Simple query helper which takes in an SGQLC Operation"""
        return self.endpoint(query=operation)
