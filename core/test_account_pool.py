#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
账号池测试脚本
用于测试账号池的自动获取新账号功能
"""

import asyncio
from wwd.pkg.account_pool.pool import AccountWithIpPoolManager


async def test_account_pool():
    """
    测试账号池功能
    """
    print("开始测试账号池功能...")
    
    # 创建账号池管理器实例
    account_pool_manager = AccountWithIpPoolManager(platform_name='ks', work_dir='core/work_dir')
    
    # 初始化账号池7
    print("正在初始化账号池...")
    await account_pool_manager.async_initialize()
    
    try:
        # 获取账号（如果账号池为空，会自动引导用户登录）
        print("正在获取账号...")
        account_with_ip = await account_pool_manager.get_account_with_ip_info()
        print(f"成功获取账号: {account_with_ip}")
        
        return account_with_ip
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        raise
    finally:
        print("测试完成")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_account_pool()) 