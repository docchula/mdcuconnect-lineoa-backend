from django.conf import settings
from linebot.v3.messaging.models import (
    RichMenuRequest,
    RichMenuSize,
    RichMenuArea,
    RichMenuBounds,
    URIAction,
)
from enum import Enum


class Message:
    GREETING = "สวัสดีคุณ {} ยินดีต้อนรับสู่ MDCU Connect ศูนย์กลางข้อมูลข่าวสาร ครบครันทั้งวิชาการ กิจกรรม และสุขภาพกายใจ สำหรับนิสิตแพทย์จุฬาฯ ทุกคน"
    REGISTER_PENDING = "กรุณากดลงทะเบียนด้านล่างเพื่อเริ่มต้นใช้งาน"
    REGISTER_SUCCESS = "ลงทะเบียนเสร็จสิ้น อย่าลืมเลือก tags หมวดที่สนใจได้ที่หน้าเมนู เพื่อให้น้อง Connect ส่งข่าวประชาสัมพันธ์ตามหมวดที่คุณ {} สนใจน้าา"

    ERROR_UNKNOWN = "ระบบไม่เข้าใจ ลองใหม่อีกครั้งนะ!"


class RichMenuNameEnum(Enum):
    REGISTER = "register"


TAP_TO_OPEN_TEXT = "Tap to open"


RICH_MENU_MAPPINGS = {
    RichMenuNameEnum.REGISTER.value: RichMenuRequest(
        size=RichMenuSize(width=2500, height=843),
        selected=False,
        name=RichMenuNameEnum.REGISTER.value,
        chat_bar_text=TAP_TO_OPEN_TEXT,
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=2500, height=843),
                action=URIAction(label="verification form", uri=settings.LIFF_URL),
            ),
        ],
    ),
}
