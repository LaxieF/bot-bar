if msg in ["!ayuda", "!help", "/help"]:
    menu = (
        "<color=#F2C94C>✨ Command Categories: ✨</color>\n"
        "<i>Type /help to see commands in that category.</i>\n\n"
        "💃 <color=#E282B7>/help emotes</color>\n"
        "🚀 <color=#7CB9E8>/help tp</color>\n"
        "🎮 <color=#A892EE>/help fun</color>\n"
        "🪙 <color=#F2C94C>/help gold</color>\n"
        "🛡️ <color=#FF7F50>/help mod</color>\n"
        "⚙️ <color=#FF4500>/help admin</color>"
    )
    await self.highrise.send_whisper(user.id, menu)
    return
    
