import logging
import os
from datetime import datetime
from pb_exporter import PbExporter

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def preprocess_infos_data(data):
    """预处理 infos 集合的数据"""
    for item in data:
        if 'created' in item:
            item['created'] = item['created'].strftime('%Y-%m-%d %H:%M:%S')
        if 'updated' in item:
            item['updated'] = item['updated'].strftime('%Y-%m-%d %H:%M:%S')
        if 'references' in item:
            item['references'] = str(item['references'])
    return data

def export_infos():
    # 获取当前目录和日期
    current_dir = os.path.dirname(os.path.abspath(__file__))
    today = datetime.now().strftime('%Y-%m-%d')
    csv_path = os.path.join(current_dir, f"{today}.csv")
    
    try:
        # 初始化导出器
        exporter = PbExporter(logger)
        logger.info(f"开始导出数据到: {csv_path}")
        
        # 定义要导出的字段
        fields = [
            "id", "created", "updated", "content", 
            "references", "report", "screenshot", 
            "tag", "url", "url_title"
        ]
        
        # 执行导出
        result = exporter.export_to_csv(
            collection_name="pbc_629947526",
            output_path=csv_path,
            fields=fields,
            filter_str="",  # 可以添加过滤条件
            preprocess_func=preprocess_infos_data
        )
        
        if result:
            file_size = os.path.getsize(csv_path)
            logger.info(f"✓ 导出成功 - {csv_path}")
            logger.info(f"  文件大小: {file_size/1024:.2f}KB")
        else:
            logger.error("导出失败")
            
    except Exception as e:
        logger.error(f"导出过程出错: {str(e)}")

if __name__ == "__main__":
    export_infos()
