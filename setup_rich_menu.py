"""
Script to create, upload image, and set default LINE Rich Menu for Chongpenyang Barista Assistant.
Usage: python setup_rich_menu.py
"""
import os
import sys
import json
import requests

from chatbot.config import settings
from chatbot.line_ui.rich_menu import prepare_rich_menu_image, get_rich_menu_payload, RICH_MENU_IMG_PATH

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def setup_rich_menu():
    print("=" * 60)
    print("  CHONGPENYANG BARISTA AI - LINE RICH MENU AUTO SETUP")
    print("=" * 60)

    token = settings.CHANNEL_ACCESS_TOKEN
    if not token:
        print("❌ [ERROR] LINE_CHANNEL_ACCESS_TOKEN is missing in .env")
        return False

    headers_json = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 1. Prepare Rich Menu Image (2500x1686, strictly <= 1MB for LINE API)
    print("\n[1/4] Preparing 2500x1686 Rich Menu Image...")
    img_path = prepare_rich_menu_image(RICH_MENU_IMG_PATH)
    file_size_kb = os.path.getsize(img_path) / 1024
    print(f"      Image ready at: {img_path} ({file_size_kb:.1f} KB)")

    # 2. Create Rich Menu Object on LINE Platform
    print("\n[2/4] Registering Rich Menu Schema with LINE Messaging API...")
    payload = get_rich_menu_payload()
    res = requests.post("https://api.line.me/v2/bot/richmenu", headers=headers_json, json=payload)
    
    if res.status_code != 200:
        print(f"❌ [ERROR] Failed to create rich menu: {res.status_code} -> {res.text}")
        return False

    rich_menu_id = res.json().get("richMenuId")
    print(f"      Created Rich Menu ID: {rich_menu_id}")

    # 3. Upload Image to the created Rich Menu
    print("\n[3/4] Uploading Rich Menu Image to LINE CDN...")
    content_type = "image/jpeg" if img_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
    headers_img = {
        "Authorization": f"Bearer {token}",
        "Content-Type": content_type
    }
    with open(img_path, "rb") as f:
        img_data = f.read()

    upload_url = f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content"
    res_upload = requests.post(upload_url, headers=headers_img, data=img_data)
    if res_upload.status_code != 200:
        print(f"❌ [ERROR] Failed to upload image: {res_upload.status_code} -> {res_upload.text}")
        return False
    print("      Image uploaded successfully!")

    # 4. Set as Default Rich Menu for all users
    print("\n[4/4] Activating as Default Rich Menu for all chat users...")
    default_url = f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}"
    res_default = requests.post(default_url, headers=headers_json)
    if res_default.status_code != 200:
        print(f"❌ [ERROR] Failed to set default rich menu: {res_default.status_code} -> {res_default.text}")
        return False

    # Optional: Clean up old rich menus
    try:
        r_list = requests.get("https://api.line.me/v2/bot/richmenu/list", headers=headers_json)
        if r_list.status_code == 200:
            for rm in r_list.json().get("richmenus", []):
                old_id = rm.get("richMenuId")
                if old_id != rich_menu_id:
                    requests.delete(f"https://api.line.me/v2/bot/richmenu/{old_id}", headers=headers_json)
    except Exception:
        pass

    print("\n" + "=" * 60)
    print(f"🎉 SUCCESS! Default Rich Menu is now ACTIVE!")
    print(f"   Rich Menu ID: {rich_menu_id}")
    print("=" * 60)
    return True

if __name__ == "__main__":
    setup_rich_menu()
