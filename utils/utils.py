import hashlib

def hash_phone(phone: str) -> str:
    """
    Hash phone number for security
    
    Args:
        phone (str): The phone number to hash
        
    Returns:
        str: The hashed phone number
    """
    return hashlib.sha256(phone.encode('utf-8')).hexdigest()