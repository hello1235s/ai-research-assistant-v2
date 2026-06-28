"""
AI智能科研辅助助手 - 安全加密模块
包含：bcrypt密码哈希 + AES API Key加密
"""

import bcrypt
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import config


# ========== bcrypt 密码哈希 ==========

def hash_password(password: str) -> str:
    """
    使用bcrypt对密码进行哈希
    返回: bcrypt哈希字符串（可直接存入数据库）
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=config.BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    验证密码是否匹配哈希值
    返回: True/False
    """
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


# ========== AES 对称加密（用于API Key） ==========

def _get_cipher():
    """获取AES加密器实例"""
    return Cipher(
        algorithms.AES(config.AES_KEY),
        modes.CBC(config.AES_IV),
        backend=default_backend()
    )


def encrypt_api_key(api_key: str) -> str:
    """
    AES加密API Key
    返回: base64编码的加密字符串（可安全存入数据库）
    """
    if not api_key:
        return None

    encryptor = _get_cipher().encryptor()
    # PKCS7填充
    data = api_key.encode('utf-8')
    padding_length = 16 - (len(data) % 16)
    padded_data = data + bytes([padding_length] * padding_length)
    # 加密
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    # base64编码
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt_api_key(encrypted_key: str) -> str:
    """
    AES解密API Key
    返回: 明文字符串
    """
    if not encrypted_key:
        return None

    try:
        decryptor = _get_cipher().decryptor()
        # base64解码
        encrypted = base64.b64decode(encrypted_key.encode('utf-8'))
        # 解密
        decrypted = decryptor.update(encrypted) + decryptor.finalize()
        # PKCS7去填充
        padding_length = decrypted[-1]
        return decrypted[:-padding_length].decode('utf-8')
    except Exception:
        return None


# ========== 便捷函数 ==========

def get_api_key_for_user(user):
    """
    获取用户可用的API Key（优先级：用户个人Key > 系统默认Key）
    user: User模型实例
    返回: API Key字符串
    """
    if user and user.api_key_encrypted:
        key = decrypt_api_key(user.api_key_encrypted)
        if key:
            return key
    return config.DEFAULT_API_KEY
