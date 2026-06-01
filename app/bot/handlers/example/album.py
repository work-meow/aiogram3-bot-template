from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder

from app.bot.filters import AlbumContains



router = Router()


async def _send_echo_album(
    message: Message,
    album: list[Message],
    caption_text: str,
) -> None:
    """Универсальная сборка и 
    отправка эхо-альбомов 
    (включая миксы)."""
    
    builder = MediaGroupBuilder(
        caption=(
            f"{caption_text} "
            f"{len(album)}"
        )
    )
    
    for msg in album:
        if msg.photo:
            builder.add_photo(
                msg.photo[-1].file_id
            )
            
        elif msg.video:
            builder.add_video(
                msg.video.file_id
            )
            
        elif msg.document:
            builder.add_document(
                msg.document.file_id
            )
            
        elif msg.audio:
            builder.add_audio(
                msg.audio.file_id
            )
                
    await message.answer_media_group(
        builder.build()
    )




@router.message(
    F.media_group_id, 
    AlbumContains("photo")
)
async def handle_photo_album(
    message: Message, 
    album: list[Message]
) -> None:
    """Обработка альбомов 
    из фотографий."""
    
    await _send_echo_album(
        message=message,
        album=album,
        caption_text="📸 Картинки:"
    )




@router.message(
    F.media_group_id,
    AlbumContains("video")
)
async def handle_video_album(
    message: Message,
    album: list[Message]
) -> None:
    """Обработка альбомов с 
    видеозаписями."""
    
    await _send_echo_album(
        message=message,
        album=album,
        caption_text="🎬 Видео:"
    )




@router.message(
    F.media_group_id,
    AlbumContains("document")
)
async def handle_document_album(
    message: Message,
    album: list[Message]
) -> None:
    """Обработка альбомов с 
    документами и файлами."""
    
    await _send_echo_album(
        message=message,
        album=album,
        caption_text="📁 Файлы:"
    )




@router.message(
    F.media_group_id,
    AlbumContains("audio")
)
async def handle_audio_album(
    message: Message,
    album: list[Message]
) -> None:
    """Обработка альбомов
    с музыкой и аудио."""
    
    await _send_echo_album(
        message=message,
        album=album,
        caption_text="🎵 Аудио:"
    )