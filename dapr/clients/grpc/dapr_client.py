# -*- coding: utf-8 -*-

"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import grpc

from dapr.conf import settings
from dapr.clients.base import DEFAULT_JSON_CONTENT_TYPE

from google.protobuf.any_pb2 import Any as GrpcAny
from google.protobuf.message import Message as GrpcMessage

from dapr.proto import api_v1, api_service_v1, common_v1
from typing import Dict, List, Optional, Union, Tuple


MetadataDict = Dict[str, List[Union[bytes, str]]]
MetadataTuple = Tuple[Tuple[str, Union[bytes, str]], ...]


class DaprResponse:
    def __init__(
        self,
        headers: Optional[MetadataTuple] = (),
        trailers: Optional[MetadataTuple] = (),
    ):
        self._headers = headers
        self._trailers = trailers

    def _from_tuple(self, metadata: MetadataTuple) -> MetadataDict:
        d = {}
        for k, v in metadata:
            d.setdefault(k, []).append(v)
        return d

    @property
    def as_headers_dict(self) -> MetadataDict:
        return self._from_tuple(self._headers)

    @property
    def as_trailers_dict(self) -> MetadataDict:
        return self._from_tuple(self._trailers)


class InvokeServiceResponse(DaprResponse):
    def __init__(
        self,
        data: GrpcAny,
        content_type: Optional[str] = None,
        headers: Optional[MetadataTuple] = (),
        trailers: Optional[MetadataTuple] = (),
    ):
        super(InvokeServiceResponse, self).__init__(headers, trailers)
        if not isinstance(data, GrpcMessage):
            raise ValueError(f"data is not protobuf message.")
        self._proto_any = data
        self._content_type = content_type

    @property
    def proto(self) -> GrpcAny:
        if not self.is_proto():
            raise ValueError(f"data is not grpc protobuf message")
        return self._proto_any

    @property
    def data(self) -> bytes:
        if self.is_proto():
            raise ValueError(f"data is not bytes")
        return self._proto_any.value

    @property
    def content_type(self) -> str:
        return self._content_type

    def is_proto(self) -> bool:
        return self._proto_any.type_url != ""

    def unpack(self, message: GrpcMessage) -> None:
        if not self._proto_any.Is(message.DESCRIPTOR):
            raise ValueError(
                f"invalid type. serialized message type: {self._proto_any.type_url}"
            )
        self._proto_any.Unpack(message)


class DaprClient:
    def __init__(self, address: Optional[str] = None):
        if not address:
            address = f"127.0.0.1:{settings.DAPR_GRPC_PORT}"
        self._channel = grpc.insecure_channel(address)
        self._stub = api_service_v1.DaprStub(self._channel)

    def __del__(self):
        self._channel.close()

    def _get_http_extension(
        self, http_verb: str, http_querystring: Optional[MetadataTuple] = ()
    ) -> common_v1.HTTPExtension:
        verb = common_v1.HTTPExtension.Verb.Value(http_verb)
        http_ext = common_v1.HTTPExtension(verb=verb)
        for key, val in http_querystring:
            http_ext.querystring[key] = val
        return http_ext

    def get_state(self, state_store_name: str, key: str) -> bytes:
        req = api_service_v1.GetStateRequest(store_name=state_store_name, key=key)
        response = self._stub.GetState(req)
        return response

    def invoke_service(
        self,
        target_id: str,
        method: str,
        data: InvokeServiceRequestData,
        metadata: Optional[MetadataTuple] = None,
        http_verb: Optional[str] = None,
        http_querystring: Optional[MetadataTuple] = None,
    ) -> InvokeServiceResponse:
        """Invoke target_id service to call method.
        :param str target_id: str to represent target App ID.
        :param str method: str to represent method name defined in target_id
        :param InvokeServiceRequestData data: bytes or Message for data which will send to target_id
        :param MetadataTuple metadata: dict to pass custom metadata to target app
        :param str http_verb: http method verb to call HTTP callee application
        :param MetadataTuple http_querystring: dict to represent querystring for
         HTTP callee application

        :returns: the response from callee
        :rtype: InvokeServiceResponse
        """
        http_ext = None
        if http_verb:
            http_ext = self._get_http_extension(http_verb, http_querystring)

        req = api_v1.InvokeServiceRequest(
            id=target_id,
            message=common_v1.InvokeRequest(
                method=method,
                data=data.proto,
                content_type=data.content_type,
                http_extension=http_ext,
            ),
        )

        response, call = self._stub.InvokeService.with_call(req, metadata=metadata)

        return InvokeServiceResponse(
            response.data,
            response.content_type,
            call.initial_metadata(),
            call.trailing_metadata(),
        )

    def save_states(self, state_store_name: str, states: List[dict]):
        """Save states to the specified state store.
        :param str state_store_name: str to represent the state store to be called.
        :param List[commonv1.StateItem]: stateitems representing the key-value pairs to be saved.

        :returns: the response from callee
        :rtype: InvokeServiceResponse
        """
        if len(state_store_name) == 0 or state_store_name is None:
            raise ValueError("State store name cannot be null or empty")
        if len(states) == 0:
            raise ValueError("States cannot be null in saving states")

        state_items = [
            commonv1.StateItem(key=state.key, value=state.value) for state in states
        ]
        req = api_v1.SaveStateRequest(store_name=storeName, states=state_items)
        self._stub.SaveState(req)
