from dapr.conf import settings
from dapr.clients.api_base import DaprApiClientBase, AppState
import dapr.proto.common.v1.common_pb2 as common_pb2 
import dapr.proto.runtime.v1.dapr_pb2_grpc as runtime_pb2
from dapr.proto.runtime.v1 import GetStateRequest, SaveStateRequest,

class DaprClientGrpc(DaprApiClientBase):
    """ A Dapr Grpc Client implementing :class:`DaprApiClientBase`"""
    def __init__(self):
        channel = 'http://127.0.0.1:{}'.format(settings.DAPR_GRPC_PORT)        
        self.client = runtime_pb2.DaprStub(channel)

    
    async def get_state(
        self, state_store_name: str, key: str
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
        request = GetStateRequest(store_name = state_store_name, key = key)
        self.client.GetState(request)


    async def save_state(
        self, state_store_name: str, app_state: ,
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
        self.client.SaveState()

    async def delete_state(
        self, state_store_name, str, key: str
    ) -> bytes:
        if state_store_name is None or len(state_store_name)==0:
            raise ValueError("State store name cannot be null or empty")
        if key is None or len(key)==0:
            raise ValueError("Key cannot be null or empty")