from aiogram import Router
from aiogram.filters import Command
from aiogram_i18n import I18nContext
from aiogram.types import (
    InputRichBlockMathematicalExpression,
    InputRichBlockSectionHeading,
    InputRichBlockBlockQuotation,
    InputRichBlockPreformatted,
    InputRichBlockParagraph,
    InputRichBlockListItem,
    InputRichBlockThinking,
    InputRichBlockDivider,
    InputRichBlockDetails,
    InputRichBlockFooter,
    InputRichBlockTable,
    InputRichBlockList,
    RichBlockTableCell,
    InputRichBlockMap,
    InputRichMessage,
    Location,
    Message,
)


from app.bot.localization import answer_rich



router = Router(name="rich")


@router.message(Command("rich-text"))
async def cmd_rich_text(msg: Message, i18n: I18nContext) -> None:
    """Текстовое rich-сообщение через helper."""
    
    await answer_rich(
        msg, i18n, "welcome-text", 
        name=msg.from_user.full_name
    )



def _cell(
    text: str, 
    header: bool = False
) -> RichBlockTableCell:
    
    return RichBlockTableCell(
        text=text,
        align="left", 
        valign="top", 
        is_header=header
    )



@router.message(Command("rich-block"))
async def cmd_rich(msg: Message, i18n: I18nContext) -> None:
    """Блочное rich-сообщение: заголовок + таблица + Thinking.
    Текст внутри блоков — обычные строки из локали (не HTML)."""
    
    await msg.answer_rich(
        rich_message=InputRichMessage(
            blocks=[
                InputRichBlockSectionHeading(
                    text=i18n.get("rich-title"),
                    size=1
                ),
                InputRichBlockTable(
                    is_striped=True,
                    cells=[
                        [
                            _cell(i18n.get("rich-col-metric"), header=True),
                            _cell(i18n.get("rich-col-value"), header=True)
                        ],
                        [_cell(i18n.get("rich-row-users")), _cell("1 240")],
                        [_cell(i18n.get("rich-row-uptime")), _cell("99.9%")],
                    ],
                ),
                InputRichBlockDivider(),
                InputRichBlockBlockQuotation(
                    blocks=[
                        InputRichBlockParagraph(
                            text=i18n.get("rich-quote")
                        )
                    ],
                    credit=i18n.get("rich-quote-author"),
                ),
                InputRichBlockDetails(
                    summary=i18n.get("rich-details-summary"),
                    blocks=[
                        InputRichBlockParagraph(
                            text=i18n.get("rich-details-body")
                        )
                    ],
                ),
                InputRichBlockList(
                    items=[
                        InputRichBlockListItem(
                            blocks=[InputRichBlockParagraph(
                                text=i18n.get("rich-list-1")
                            )]
                        ),
                        InputRichBlockListItem(
                            blocks=[InputRichBlockParagraph(
                                text=i18n.get("rich-list-2")
                            )]
                        ),
                    ],
                ),
                InputRichBlockPreformatted(
                    text=(
                        """
                        "await bot.send_rich_message( "
                            chat_id, rich_message=...
                        )
                        """
                    ),
                    language="python",
                ),
                InputRichBlockMathematicalExpression(
                    expression="p_{99} = 42ms",
                ),
                InputRichBlockMap(
                    location=Location(
                        latitude=55.7558, 
                        longitude=37.6173
                    ),
                    zoom=12,
                    width=600,
                    height=400,
                ),
                InputRichBlockThinking(text=i18n.get("rich-thinking")),
                InputRichBlockFooter(text=i18n.get("rich-footer")),
            ],
        ),
    )
