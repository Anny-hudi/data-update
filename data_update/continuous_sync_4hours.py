#!/usr/bin/env python3
"""
连续数据同步脚本 - 每4小时同步一次数据
定时同步赛狐ERP数据到本地数据库
"""
import sys
import os
import time
from datetime import datetime, date, timedelta
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from src.services.data_sync_service import data_sync_service
from src.database.connection import db_manager

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/hudi_data/sync_saihu_erp/data_update/sync_4hours.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ContinuousSync:
    """连续数据同步服务"""
    
    def __init__(self):
        self.sync_count = 0
        self.start_time = datetime.now()
        
    def print_header(self):
        """打印同步头部信息"""
        print("\n" + "="*80)
        print("🔄 赛狐ERP数据连续同步服务 - 4小时间隔")
        print(f"📅 启动时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 同步目标: FBA库存 + 库存明细 + 产品分析数据")
        print(f"⏰ 同步间隔: 4小时")
        print("="*80)
        
    def sync_all_data(self):
        """执行所有数据同步"""
        sync_time = datetime.now()
        self.sync_count += 1
        
        print(f"\n🔄 第 {self.sync_count} 次同步 - {sync_time.strftime('%H:%M:%S')}")
        print("-" * 60)
        
        results = {
            'fba_inventory': False,
            'warehouse_inventory': False,
            'product_analytics_yesterday': False,
            'product_analytics_7days': False
        }
        
        try:
            # 1. 同步FBA库存数据（当天全量替换）
            print("📦 同步FBA库存数据...")
            fba_result = data_sync_service.sync_fba_inventory_today()
            results['fba_inventory'] = fba_result
            status = "✅ 成功" if fba_result else "❌ 失败"
            print(f"   FBA库存同步: {status}")
            
            # 延迟1秒避免API频率限制
            time.sleep(1)
            
            # 2. 同步库存明细数据（当天全量替换）
            print("🏠 同步库存明细数据...")
            warehouse_result = data_sync_service.sync_warehouse_inventory_today()
            results['warehouse_inventory'] = warehouse_result
            status = "✅ 成功" if warehouse_result else "❌ 失败"
            print(f"   库存明细同步: {status}")
            
            # 延迟1秒避免API频率限制
            time.sleep(1)
            
            # 3. 同步前一天产品分析数据（增量）
            print("📊 同步前一天产品分析数据...")
            yesterday_result = data_sync_service.sync_product_analytics_yesterday()
            results['product_analytics_yesterday'] = yesterday_result
            status = "✅ 成功" if yesterday_result else "❌ 失败"
            print(f"   昨日产品分析: {status}")
            
            # 延迟1秒避免API频率限制
            time.sleep(1)
            
            # 4. 更新前7天产品分析数据（增量）
            print("📈 更新前7天产品分析数据...")
            seven_days_result = data_sync_service.sync_product_analytics_last_seven_days()
            results['product_analytics_7days'] = seven_days_result
            status = "✅ 成功" if seven_days_result else "❌ 失败"
            print(f"   7天产品分析: {status}")
            
        except Exception as e:
            logger.error(f"数据同步异常: {e}")
            print(f"❌ 同步过程发生异常: {e}")
        
        # 打印同步总结
        success_count = sum(1 for result in results.values() if result)
        print(f"\n📊 本次同步结果: {success_count}/4 成功")
        
        if success_count == 4:
            print("🎉 所有数据同步成功！")
        elif success_count > 0:
            print("⚠️ 部分数据同步成功")
        else:
            print("❌ 所有数据同步失败")
            
        return results
    
    def check_database_status(self):
        """检查数据库状态"""
        try:
            print("\n💾 检查数据库状态...")
            
            # 检查各表的数据量
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # FBA库存表
                    cursor.execute("SELECT COUNT(*) FROM fba_inventory")
                    fba_count = cursor.fetchone()[0]
                    
                    # 库存明细表
                    cursor.execute("SELECT COUNT(*) FROM inventory_details")
                    warehouse_count = cursor.fetchone()[0]
                    
                    # 产品分析表
                    cursor.execute("SELECT COUNT(*) FROM product_analytics")
                    analytics_count = cursor.fetchone()[0]
                    
                    # 今日新增数据
                    today = date.today().strftime('%Y-%m-%d')
                    cursor.execute(f"SELECT COUNT(*) FROM fba_inventory WHERE DATE(created_at) = '{today}'")
                    fba_today = cursor.fetchone()[0]
                    
                    cursor.execute(f"SELECT COUNT(*) FROM inventory_details WHERE DATE(created_at) = '{today}'")
                    warehouse_today = cursor.fetchone()[0]
                    
                    cursor.execute(f"SELECT COUNT(*) FROM product_analytics WHERE DATE(created_at) = '{today}'")
                    analytics_today = cursor.fetchone()[0]
            
            print(f"   📦 FBA库存数据: {fba_count} 条 (今日新增: {fba_today})")
            print(f"   🏠 库存明细数据: {warehouse_count} 条 (今日新增: {warehouse_today})")
            print(f"   📊 产品分析数据: {analytics_count} 条 (今日新增: {analytics_today})")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据库状态检查失败: {e}")
            return False
    
    def print_runtime_stats(self):
        """打印运行时统计"""
        runtime = datetime.now() - self.start_time
        hours = int(runtime.total_seconds() // 3600)
        minutes = int((runtime.total_seconds() % 3600) // 60)
        seconds = int(runtime.total_seconds() % 60)
        
        print(f"\n⏱️ 运行统计:")
        print(f"   已运行时间: {hours:02d}:{minutes:02d}:{seconds:02d}")
        print(f"   完成同步次数: {self.sync_count}")
        if self.sync_count > 0:
            avg_interval = runtime.total_seconds() / self.sync_count
            print(f"   平均同步间隔: {avg_interval:.1f}秒")
    
    def run(self):
        """运行连续同步服务"""
        self.print_header()
        
        try:
            while True:
                # 执行数据同步
                sync_results = self.sync_all_data()
                
                # 检查数据库状态
                self.check_database_status()
                
                # 打印运行统计
                self.print_runtime_stats()
                
                print(f"\n💤 等待4小时后进行下次同步...")
                print("-" * 80)
                
                # 等待4小时 (4 * 60 * 60 = 14400秒)
                time.sleep(14400)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 用户手动停止同步服务")
            self.print_runtime_stats()
            print("✅ 同步服务已安全退出")
        except Exception as e:
            logger.error(f"连续同步服务异常: {e}")
            print(f"\n❌ 同步服务异常退出: {e}")
        finally:
            print("👋 感谢使用赛狐ERP数据同步服务")

def main():
    """主函数"""
    print("🚀 启动赛狐ERP连续数据同步服务")
    print("💡 提示: 按 Ctrl+C 停止同步服务")
    
    sync_service = ContinuousSync()
    sync_service.run()

if __name__ == "__main__":
    main()