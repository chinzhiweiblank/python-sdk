from dapr.clients.api_base import DaprApiClientBase, AppState
from dapr.proto.common.v1.common_pb2
from dapr.proto.runtime.v1.dapr_pb2_grpc import DaprStub


class DaprClientGrpc(DaprApiClientBase):
    """ A Dapr Grpc Client implementing :class:`DaprApiClientBase`"""
    def __init__(self):
        self.client = DaprStub

    
    async def get_state(
        self, state_store_name: str, key: str
    ) -> bytes:
        """Get state.

        :param str state_store_name: str to represent name of state store.
        :param str key: str to represent key of state to be retrieved.
        :rtype: bytes
        """


    async def save_state(
        self, state_store_name: str, app_state: AppState,
    ) -> bytes:
        """Get state.

        :param str state_store_name: str to represent name of state store.
        :param str key: str to represent key of state to be retrieved.
        :rtype: bytes
        """
        if state_store_name is None or len(state_store_name)==0:
            raise ValueError("State store name cannot be null or empty")
        if key is None or len(key)==0:
            raise ValueError("Key cannot be null or empty")
        

    async def delete_state(
        self, state_store_name, str, key: str
    )
