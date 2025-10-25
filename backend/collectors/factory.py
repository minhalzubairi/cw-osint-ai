"""
Collector Factory
Creates appropriate collector instances based on source type
"""

from typing import Dict, Any, List
from backend.collectors.github_collector import GitHubCollector
# Import other collectors as needed
# from backend.collectors.rss_collector import RSSCollector


class CollectorFactory:
    """Factory for creating data collectors"""
    
    _collectors = {
        'github': GitHubCollector,
        # 'rss': RSSCollector,
        # Add more collectors here
    }
    
    @classmethod
    def create_collector(cls, source_type: str, config: Dict[str, Any]):
        """
        Create a collector instance for the given source type
        
        Args:
            source_type: Type of data source
            config: Configuration for the collector
            
        Returns:
            Collector instance
            
        Raises:
            ValueError: If source_type is not supported
        """
        collector_class = cls._collectors.get(source_type)
        
        if not collector_class:
            raise ValueError(
                f"Unsupported source type: {source_type}. "
                f"Available types: {', '.join(cls._collectors.keys())}"
            )
        
        return collector_class(config)
    
    @classmethod
    def get_available_collectors(cls) -> List[str]:
        """Get list of available collector types"""
        return list(cls._collectors.keys())
    
    @classmethod
    def register_collector(cls, source_type: str, collector_class):
        """
        Register a new collector type
        
        Args:
            source_type: Type identifier for the collector
            collector_class: Collector class to register
        """
        cls._collectors[source_type] = collector_class
