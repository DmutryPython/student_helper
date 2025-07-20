class ReportGenerator:
    @staticmethod
    def generate(structure: dict, parasites: dict) -> str:
        """Генерация финального отчета"""
        report = ["📊 **Анализ устного ответа**\n"]

        # Структурный анализ
        report.append("🧩 **Структура ответа:**")
        if structure["missing_parts"]:
            report.append(f"❌ Отсутствуют: {', '.join(structure['missing_parts'])}")
            report.append(f"✅ Полнота: {structure['score'] * 100:.1f}%")

            # Слова-паразиты
            report.append("\n🗣️ **Речевые особенности:**")
            report.append(f"🚫 Слова-паразиты: {parasites['total']} случаев")
            report.append(f"📊 Частота: {parasites['frequency']:.1f}%")

            # Рекомендации
            report.append("\n💡 **Рекомендации для улучшения:**")
            if structure["missing_parts"]:
                report.append("- Обязательно включайте все части ответа: введение, основную часть и заключение")
            if parasites["total"] > 5:
                report.append("- Практикуйте осознанную речь: делайте паузы вместо слов-паразитов")

        return "\n".join(report)