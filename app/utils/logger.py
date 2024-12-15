from loguru import logger

def get_logger(name: str):
    """
    获取logger实例
    
    Args:
        name: 模块名称
        
    Returns:
        logger实例
    """
    return logger.bind(module=name)
