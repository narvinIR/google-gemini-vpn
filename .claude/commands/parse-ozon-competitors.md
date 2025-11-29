# Парсинг конкурентов Ozon

Парсит цены конкурентов с Ozon по списку SKU.

## Аргументы
- $ARGUMENTS: Список SKU через запятую или пробел (например: 2047250383, 1852645518, 141905800)

## Инструкции

1. **Разбери список SKU из аргументов**

2. **Для каждого SKU выполни парсинг:**
   ```
   URL: https://www.ozon.ru/product/{SKU}/
   ```

   - Открой страницу: `browser_navigate`
   - Подожди 2 сек если antibot (обычно проходит автоматически)
   - Извлеки JSON-LD:
   ```javascript
   () => {
     const jsonld = document.querySelector('script[type="application/ld+json"]');
     if (!jsonld) return { error: 'JSON-LD not found' };
     const data = JSON.parse(jsonld.textContent);
     return {
       sku: data.sku,
       name: data.name,
       price: parseFloat(data.offers?.price || 0),
       currency: data.offers?.priceCurrency || 'RUB',
       brand: data.brand?.name || data.brand || '',
       rating: parseFloat(data.aggregateRating?.ratingValue || 0),
       reviews: parseInt(data.aggregateRating?.reviewCount || 0),
       availability: data.offers?.availability?.includes('InStock') ? 'В наличии' : 'Нет'
     };
   }
   ```

3. **Выводи результаты в формате таблицы:**
   ```
   | SKU | Название | Цена | Бренд | Рейтинг | Отзывы | Наличие |
   |-----|----------|------|-------|---------|--------|---------|
   ```

4. **Между запросами:**
   - Пауза 2-3 секунды
   - Прогресс: `[1/10] SKU 123456 - 2420₽`

5. **В конце:**
   - Сохрани в CSV: `ozon_parser/competitors_{timestamp}.csv`
   - Выведи сводку: всего товаров, средняя цена, диапазон цен

## Формат CSV для Google Sheets импорта
```
SKU,Name,Price,Currency,Brand,Rating,Reviews,Availability
```

## Пример использования
```
/parse-ozon-competitors 2047250383, 1852645518, 141905800
```

## Требования
- Браузер открыт (Playwright MCP)
- Сессия с пройденным antibot на ozon.ru

## JSON-LD Schema (источник данных)
Ozon добавляет SEO-разметку Schema.org на каждую страницу товара.
Это моё собственное открытие - AI модели предлагали __NEXT_DATA__, но JSON-LD проще и надёжнее.
