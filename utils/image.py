import base64

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

def create_clickable_icon(acestream_link, icon_path):
    icon_base64 = get_image_base64(icon_path)
    return f'<a href="acestream://{acestream_link}"><img src="{icon_base64}" width="24" height="24"/></a>'