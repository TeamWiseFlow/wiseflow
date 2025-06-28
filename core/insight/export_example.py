import logging
import os
from .pb_exporter import PbExporter


# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection(exporter):
    """测试PocketBase连接并列出所有可用集合的数据"""
    try:
        # 输出服务器连接信息
        logger.info("=== PocketBase 连接信息 ===")
        logger.info(f"服务器地址: {exporter.client.base_url}")
        logger.info(f"认证状态: {'已认证' if exporter.client.auth_store.token else '未认证'}")
        
        # 直接尝试获取一个已知的集合
        try:
            # 尝试读取 pbc_629947526 集合
            collection_name = "pbc_629947526"
            logger.info(f"\n=== 读取集合: {collection_name} ===")
            
            data = exporter.read(
                collection_name=collection_name,
                fields=None,
                expand=None,
                filter='',
                skiptotal=True
            )
            
            logger.info(f"  - 记录数量: {len(data)}")
            if data:
                # 显示第一条记录的所有字段
                logger.info("  - 可用字段:")
                for key in data[0].keys():
                    if not key.startswith('_'):  # 跳过内部字段
                        logger.info(f"    * {key}")
                logger.info("  - 样本数据 (第一条记录):")
                sample_data = {k: v for k, v in data[0].items() if not k.startswith('_')}
                logger.info(f"    {sample_data}")
            
            logger.info("-" * 50)
            return True
            
        except Exception as e:
            logger.error(f"读取集合失败: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"× PocketBase连接失败: {str(e)}")
        return False

def test_csv_export(exporter, current_dir):
    """测试CSV导出功能"""
    try:
        csv_path = os.path.join(current_dir, "users_test.csv")
        logger.info(f"开始导出CSV到: {csv_path}")
        
        result = exporter.export_to_csv(
            collection_name="users",
            output_path=csv_path,
            fields=["id", "username", "email", "created"],
            filter_str="created >= '2023-01-01'"  # 添加一个过滤条件作为测试
        )
        
        if result and os.path.exists(csv_path):
            file_size = os.path.getsize(csv_path)
            logger.info(f"✓ CSV导出成功 (文件大小: {file_size/1024:.2f}KB)")
            return True
        return False
    except Exception as e:
        logger.error(f"× CSV导出失败: {str(e)}")
        return False

def test_excel_export(exporter, current_dir):
    """测试Excel导出功能"""
    try:
        excel_path = os.path.join(current_dir, "users_test.xlsx")
        logger.info(f"开始导出Excel到: {excel_path}")
        
        result = exporter.export_to_excel(
            collection_name="users",
            output_path=excel_path,
            fields=["id", "username", "email", "created"],
            sheet_name="Users Data"
        )
        
        if result and os.path.exists(excel_path):
            file_size = os.path.getsize(excel_path)
            logger.info(f"✓ Excel导出成功 (文件大小: {file_size/1024:.2f}KB)")
            return True
        return False
    except Exception as e:
        logger.error(f"× Excel导出失败: {str(e)}")
        return False

def preprocess_infos_data(data):
    """预处理 infos 集合的数据"""
    for item in data:
        # 转换时间格式
        if 'created' in item:
            item['created'] = item['created'].strftime('%Y-%m-%d %H:%M:%S')
        if 'updated' in item:
            item['updated'] = item['updated'].strftime('%Y-%m-%d %H:%M:%S')
        # 将嵌套的 references 转为字符串
        if 'references' in item:
            item['references'] = str(item['references'])
    return data

def test_infos_export(exporter, current_dir):
    """测试导出 infos 集合"""
    try:
        # 导出为CSV
        csv_path = os.path.join(current_dir, "infos_export.csv")
        logger.info(f"开始导出 infos 到CSV: {csv_path}")
        
        fields = ["id", "created", "updated", "content", "references", 
                 "report", "screenshot", "tag", "url", "url_title"]
        
        result = exporter.export_to_csv(
            collection_name="pbc_629947526",
            output_path=csv_path,
            fields=fields,
            filter_str="",
            preprocess_func=preprocess_infos_data
        )
        
        if result and os.path.exists(csv_path):
            file_size = os.path.getsize(csv_path)
            logger.info(f"✓ CSV导出成功 (文件大小: {file_size/1024:.2f}KB)")
            return True
        return False
    except Exception as e:
        logger.error(f"× CSV导出失败: {str(e)}")
        return False

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info("=== 开始导出测试 ===")
    
    # 初始化导出器
    try:
        exporter = PbExporter(logger)
        logger.info("✓ 导出器初始化成功")
    except Exception as e:
        logger.error(f"× 导出器初始化失败: {str(e)}")
        return
    
    # 执行连接测试
    if test_connection(exporter):
        # 如果连接成功，执行导出测试
        test_infos_export(exporter, current_dir)
    
    logger.info("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
