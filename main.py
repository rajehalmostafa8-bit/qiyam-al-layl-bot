
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

QUESTIONS = [
    {
        "question": "كم عدد ركعات صلاة الوتر؟",
        "options": ["ركعة واحدة على الأقل", "خمس ركعات فقط", "سبع ركعات فقط"],
        "correct": 0,
        "explanation": "صلاة الوتر أقلها ركعة واحدة، ويجوز أداؤها بأكثر من ذلك.",
    },
    {
        "question": "متى يبدأ وقت قيام الليل؟",
        "options": [
            "بعد صلاة العشاء إلى طلوع الفجر",
            "بعد شروق الشمس فقط",
            "وقت الظهر فقط",
        ],
        "correct": 0,
        "explanation": "يمتد وقت قيام الليل من بعد صلاة العشاء إلى طلوع الفجر.",
    },
    {
        "question": "ما أفضل وقت لقيام الليل؟",
        "options": [
            "الثلث الأخير من الليل",
            "وقت الظهر",
            "بعد شروق الشمس",
        ],
        "correct": 0,
        "explanation": "ورد في الحديث فضل الثلث الأخير من الليل.",
    },
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌙 ابدأ الاختبار", callback_data="quiz")],
        [InlineKeyboardButton("📖 معلومات عن قيام الليل", callback_data="info")],
    ]
    await update.message.reply_text(
        "🌙 أهلاً بك في بوت قيام الليل\n\n"
        "تعلّم واختبر معلوماتك الدينية بأسئلة قصيرة.\n"
        "اختر ما تريد من القائمة:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.data == "info":
        await query.edit_message_text(
            "🌙 قيام الليل\n\n"
            "صلاة تطوّع تُصلّى بعد العشاء إلى طلوع الفجر، "
            "ومنها التهجّد بعد النوم.\n\n"
            "ابدأ بما تستطيع، وحافظ على الإخلاص والاستمرار."
        )
        return

    if query.data == "quiz":
        context.user_data["question_index"] = 0
        context.user_data["score"] = 0
        await send_question(query, context)


async def send_question(query, context):
    index = context.user_data["question_index"]

    if index >= len(QUESTIONS):
        score = context.user_data["score"]
        keyboard = [[
            InlineKeyboardButton("🔄 أعد الاختبار", callback_data="quiz")
        ]]
        await query.edit_message_text(
            f"🌙 انتهى الاختبار!\n\n"
            f"نتيجتك: {score} من {len(QUESTIONS)}\n\n"
            "بارك الله فيك، وواصل التعلّم.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    question = QUESTIONS[index]
    keyboard = [
        [
            InlineKeyboardButton(
                option, callback_data=f"answer:{i}"
            )
        ]
        for i, option in enumerate(question["options"])
    ]

    await query.edit_message_text(
        f"🌙 السؤال {index + 1} من {len(QUESTIONS)}\n\n"
        f"{question['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def answer_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("answer:"):
        return

    index = context.user_data.get("question_index", 0)
    if index >= len(QUESTIONS):
        return

    selected = int(query.data.split(":")[1])
    question = QUESTIONS[index]

    if selected == question["correct"]:
        context.user_data["score"] = (
            context.user_data.get("score", 0) + 1
        )
        result = "✅ إجابة صحيحة!"
    else:
        result = (
            "❌ ليست الإجابة الصحيحة.\n"
            f"الإجابة الصحيحة: "
            f"{question['options'][question['correct']]}"
        )

    context.user_data["question_index"] = index + 1

    keyboard = [[
        InlineKeyboardButton("➡️ السؤال التالي", callback_data="next")
    ]]

    await query.edit_message_text(
        f"{result}\n\n💡 {question['explanation']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def next_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    await send_question(query, context)


def main():
    if not TOKEN:
        raise RuntimeError(
            "يرجى ضبط متغير البيئة TELEGRAM_BOT_TOKEN قبل التشغيل."
        )

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(
        answer_handler, pattern=r"^answer:"
    ))
    app.add_handler(CallbackQueryHandler(
        next_handler, pattern=r"^next$"
    ))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("بوت قيام الليل جاهز للتشغيل.")
    app.run_polling()


if __name__ == "__main__":
    main()
    
