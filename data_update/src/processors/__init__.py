# processors模块初始化
from .base_processor import BaseProcessor
from .product_analytics_processor import ProductAnalyticsProcessor
from .fba_inventory_processor import FbaInventoryProcessor
from .inventory_details_processor import InventoryDetailsProcessor

__all__ = [
    'BaseProcessor',
    'ProductAnalyticsProcessor',
    'FbaInventoryProcessor',
    'InventoryDetailsProcessor'
]