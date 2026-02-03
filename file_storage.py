# backend/app/core/file_storage.py
import os
import uuid

class FileStorage:
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        # 确保目录存在，如果不存在则创建
        # 在 Docker 映射模式下，这通常对应宿主机的 /store_scrm-FTP
        if not os.path.exists(self.upload_dir):
            try:
                os.makedirs(self.upload_dir, exist_ok=True)
            except Exception as e:
                print(f"Warning: Could not create upload directory {self.upload_dir}. Error: {e}")

    def save_file(self, file_content: bytes, original_filename: str) -> str:
        """
        保存文件到本地存储
        :param file_content: 文件的二进制内容
        :param original_filename: 原始文件名
        :return: 保存后的新文件名 (UUID)
        """
        # 1. 生成唯一文件名，保留原始扩展名
        if '.' in original_filename:
            ext = original_filename.split('.')[-1]
        else:
            ext = "jpg" # 默认后缀
            
        new_filename = f"{uuid.uuid4()}.{ext}"
        
        # 2. 拼接完整路径
        file_path = os.path.join(self.upload_dir, new_filename)

        # 3. 写入文件
        with open(file_path, "wb") as f:
            f.write(file_content)
            
        return new_filename