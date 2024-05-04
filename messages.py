GREETING = """бот для ведения личных расходов

команды:
*/start* - приветственное сообщение
*/stats* - статистика по расходам
*/add* - добавить строку расходов, пример: "/add 500 б" (добавить 500 рублей в категорию бензин)
*/categories* - посмотреть доступные категории
"""

def get_stats(today_spending: int=0, total_spending: int=0, **category_spendings):
    msg = f"""статистика

расходы за сегодня
*{today_spending} руб*

расходы за все время
*{total_spending} руб*

расходы по категориям
"""
    for c, s in category_spendings.items():
        msg += f"{c} - *{s} руб*\n"
    return msg

def get_categories(categories):
    msg = f"""
категории
"""
    for category_long, category_short in categories.items():
        msg += f"*{category_short}* {category_long}\n"
    return msg
