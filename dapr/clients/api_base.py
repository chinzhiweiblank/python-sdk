# -*- coding: utf-8 -*-

"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

@dataclass
class AppState:
    key: str
    value: any


class DaprApiClientBase(ABC):
    """ A base class that represents Dapr Client. """
    @abstractmethod
    async def get_state(
        self, state_store_name: str, key: str
    ) -> bytes:
    ...

    @abstractmethod
    async def save_state(
        self, state_store_name: str, app_state: AppState,
    ) -> bytes:
    ...
    
    @abstractmethod
    async def delete_state(
        self, state_store_name, str, key: str
    )
