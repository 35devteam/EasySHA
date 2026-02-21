
# core/hash_calculator.py
import hashlib
from pathlib import Path
from typing import Dict, Optional

class HashCalculator:
    """计算文件哈希值的服务"""
    
    def __init__(self, algorithm: str = "sha256"):
        self.algorithm = algorithm
        self._hash_funcs = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512
        }
    
    def calculate(self, file_path: str, chunk_size: int = 8192) -> Optional[Dict[str, str]]:
        """
        计算文件的哈希值
        返回包含多种哈希算法的字典
        """
        file_path = Path(file_path)
        if not file_path.exists() or not file_path.is_file():
            return None
        
        # 初始化所有哈希对象
        hashes = {name: func() for name, func in self._hash_funcs.items()}
        
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    for h in hashes.values():
                        h.update(chunk)
            
            # 返回十六进制结果
            return {name: h.hexdigest() for name, h in hashes.items()}
        
        except (IOError, PermissionError) as e:
            print(f"读取文件出错 {file_path}: {e}")
            return None
    
    def calculate_single(self, file_path: str, algorithm: str = "sha256") -> Optional[str]:
        """只计算指定算法的哈希值"""
        if algorithm not in self._hash_funcs:
            raise ValueError(f"不支持的算法: {algorithm}")
        
        file_path = Path(file_path)
        if not file_path.exists():
            return None
        
        hash_obj = self._hash_funcs[algorithm]()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        
        except (IOError, PermissionError):
            return None