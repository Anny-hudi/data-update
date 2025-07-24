"""
产品分析数据模型
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any
import json
from .base import BaseModel

class ProductAnalytics(BaseModel):
    """产品分析数据模型"""
    
    def __init__(self,
                 id: Optional[int] = None,
                 product_id: str = None,
                 asin: str = None,
                 sku: str = None,
                 parent_asin: str = None,
                 spu: str = None,
                 msku: str = None,
                 data_date: date = None,
                 sales_amount: Optional[Decimal] = None,
                 sales_quantity: Optional[int] = None,
                 impressions: Optional[int] = None,
                 clicks: Optional[int] = None,
                 conversion_rate: Optional[Decimal] = None,
                 acos: Optional[Decimal] = None,
                 marketplace_id: str = None,
                 dev_name: str = None,
                 operator_name: str = None,
                 metrics_json: Optional[str] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 **kwargs):
        """初始化产品分析数据"""
        self.id = id
        self.product_id = product_id
        self.asin = asin
        self.sku = sku
        self.parent_asin = parent_asin
        self.spu = spu
        self.msku = msku
        self.data_date = data_date
        self.sales_amount = sales_amount or Decimal('0.00')
        self.sales_quantity = sales_quantity or 0
        self.impressions = impressions or 0
        self.clicks = clicks or 0
        self.conversion_rate = conversion_rate or Decimal('0.0000')
        self.acos = acos or Decimal('0.0000')
        self.marketplace_id = marketplace_id
        self.dev_name = dev_name
        self.operator_name = operator_name
        self.metrics_json = metrics_json
        self.created_at = created_at
        self.updated_at = updated_at
        
        # 额外的指标数据
        self._additional_metrics = kwargs
    
    def set_metrics(self, metrics: Dict[str, Any]) -> None:
        """设置额外的指标数据"""
        self._additional_metrics.update(metrics)
        self.metrics_json = json.dumps(self._additional_metrics, default=str, ensure_ascii=False)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取额外的指标数据"""
        if self.metrics_json:
            try:
                return json.loads(self.metrics_json)
            except json.JSONDecodeError:
                return {}
        return self._additional_metrics or {}
    
    def calculate_ctr(self) -> Decimal:
        """计算点击率 (CTR = clicks / impressions)"""
        if self.impressions and self.impressions > 0:
            return Decimal(str(self.clicks / self.impressions))
        return Decimal('0.0000')
    
    def calculate_revenue_per_click(self) -> Decimal:
        """计算每次点击收入 (RPC = sales_amount / clicks)"""
        if self.clicks and self.clicks > 0:
            return self.sales_amount / self.clicks
        return Decimal('0.00')
    
    def is_valid(self) -> bool:
        """验证数据有效性"""
        # 至少需要有ASIN
        if not self.asin:
            return False
            
        if not self.data_date:
            return False
        
        if self.sales_amount is not None and self.sales_amount < 0:
            return False
        
        if self.sales_quantity is not None and self.sales_quantity < 0:
            return False
        
        if self.conversion_rate is not None and (self.conversion_rate < 0 or self.conversion_rate > 100):
            return False
        
        if self.acos is not None and self.acos < 0:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        
        # 处理日期类型
        if isinstance(self.data_date, date):
            data['data_date'] = self.data_date.isoformat()
        
        # 处理Decimal类型
        for key in ['sales_amount', 'conversion_rate', 'acos']:
            if key in data and isinstance(data[key], Decimal):
                data[key] = float(data[key])
        
        return data
    
    @classmethod
    def from_api_response(cls, api_data: Dict[str, Any], target_date: Optional['date'] = None) -> 'ProductAnalytics':
        """从API响应数据创建实例"""
        # 字段映射 - 根据实际API响应字段名
        field_mapping = {
            'asinList': 'asin',  # 取第一个ASIN
            'skuList': 'sku',  # 取第一个SKU  
            'parentAsinList': 'parent_asin',  # 取第一个父ASIN
            'spu': 'spu',
            'mskuList': 'msku',  # 取第一个MSKU
            'salePriceThis': 'sales_amount',
            'productTotalNumThis': 'sales_quantity',
            'adImpressionsThis': 'impressions',
            'adClicksThis': 'clicks',
            'conversionRateThis': 'conversion_rate', 
            'acosThis': 'acos',
            'marketplaceIdList': 'marketplace_id',  # 取第一个市场ID
            'devNameList': 'dev_name',  # 取第一个开发者名称
            'operatorNameList': 'operator_name'  # 取第一个操作员名称
        }
        
        mapped_data = {}
        additional_metrics = {}
        
        for api_key, api_value in api_data.items():
            if api_key in field_mapping:
                mapped_key = field_mapping[api_key]
                
                # 处理列表类型字段
                if mapped_key in ['asin', 'sku', 'parent_asin', 'msku', 'marketplace_id', 'dev_name', 'operator_name'] and isinstance(api_value, list):
                    api_value = api_value[0] if api_value else None
                
                # 类型转换
                if mapped_key == 'data_date' and isinstance(api_value, str):
                    from datetime import datetime
                    mapped_data[mapped_key] = datetime.strptime(api_value, '%Y-%m-%d').date()
                elif mapped_key in ['sales_amount', 'conversion_rate', 'acos']:
                    try:
                        mapped_data[mapped_key] = Decimal(str(api_value)) if api_value is not None and api_value != '' else Decimal('0.00')
                    except (ValueError, TypeError):
                        mapped_data[mapped_key] = Decimal('0.00')
                elif mapped_key in ['sales_quantity', 'impressions', 'clicks']:
                    try:
                        mapped_data[mapped_key] = int(api_value) if api_value is not None and api_value != '' else 0
                    except (ValueError, TypeError):
                        mapped_data[mapped_key] = 0
                else:
                    mapped_data[mapped_key] = api_value
            else:
                # 未映射的字段作为额外指标
                additional_metrics[api_key] = api_value
        
        # 如果传入了目标日期，使用目标日期覆盖
        if target_date:
            mapped_data['data_date'] = target_date
        
        instance = cls(**mapped_data)
        if additional_metrics:
            instance.set_metrics(additional_metrics)
        
        return instance
    
    def get_unique_key(self) -> tuple:
        """获取唯一键用于去重"""
        return (self.product_id, self.data_date)
    
    def __str__(self) -> str:
        return f"ProductAnalytics(product_id={self.product_id}, date={self.data_date}, sales={self.sales_amount})"