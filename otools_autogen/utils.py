from functools import wraps
import logging
from datetime import datetime
import os
import base64
from PIL import Image
from io import BytesIO


def image_to_base64_inline(image_path: str) -> str:
    """
    Converts an image file to a Base64-encoded inline data URL.

    Args:
        image_path (str): The file path to the image to be converted.

    Returns:
        str: A Base64-encoded string representing the image in the format:
             "data:image/png;base64,<base64_encoded_data>".

    Raises:
        FileNotFoundError: If the specified image file does not exist.
        IOError: If the image file cannot be opened or processed.
    """
    with Image.open(image_path) as img:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        inline_base64 = f"data:image/png;base64,{img_base64}"
        return inline_base64
    

def only_direct(func):
    """
    A decorator that ensures the decorated asynchronous function is only executed 
    if the `ctx` argument is either not provided or does not have a `topic_id` attribute.

    If `ctx` is provided and has a `topic_id` attribute, the function will return `None` 
    instead of executing the decorated function.

    Args:
        func (Callable): The asynchronous function to be decorated.

    Returns:
        Callable: The wrapped asynchronous function.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        ctx = kwargs.get("ctx", None)
        if ctx is None and len(args) >= 3:
            ctx = args[2]
        if ctx is None or ctx.topic_id is None:
            return await func(*args, **kwargs)
        else:
            return None
    return wrapper