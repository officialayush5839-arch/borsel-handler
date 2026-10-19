"""
Abstract Base Collector Interface
Standardized plugin architecture for all market data ingestion sources.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from borsel_handler.core.models import NormalizedNewsRecord


class BaseCollector(ABC):
    """
    Contract that all data collectors must satisfy.
    Ensures decoupled fetching, parsing, and normalization.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable identifier for the data source."""
        pass

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Type category e.g. 'rss', 'bse_announcement', 'nse_announcement'."""
        pass

    @abstractmethod
    async def fetch(self, cutoff: Optional[datetime] = None) -> List[NormalizedNewsRecord]:
        """
        Executes data retrieval, parsing, and normalization.
        Must emit a list of validated NormalizedNewsRecord objects.
        """
        pass
