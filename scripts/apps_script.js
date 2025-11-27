/**
 * Ozon Parser - Google Apps Script
 *
 * Добавь этот код в таблицу Google Sheets:
 * 1. Расширения → Apps Script
 * 2. Вставь этот код
 * 3. Сохрани
 * 4. Добавь кнопку: Вставка → Рисунок → нарисуй кнопку
 * 5. Назначь функцию parseOzon на кнопку
 */

// URL API на Northflank (АКТИВНЫЙ)
const API_URL = "https://api--ozon-parser--44tkc9lm6yzj.code.run";

/**
 * Запуск парсинга
 * Вызывается кнопкой в таблице
 */
function parseOzon() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const spreadsheetId = spreadsheet.getId();
  const sheetName = "Парсинг товаров";

  // Проверяем что лист существует
  const sheet = spreadsheet.getSheetByName(sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Лист "${sheetName}" не найден!`);
    return;
  }

  // Считаем количество SKU
  const lastRow = sheet.getLastRow();
  const skuCount = lastRow - 1; // минус заголовок

  if (skuCount < 1) {
    SpreadsheetApp.getUi().alert("Нет SKU для парсинга! Добавь артикулы в колонку A.");
    return;
  }

  // Подтверждение
  const ui = SpreadsheetApp.getUi();
  const response = ui.alert(
    "Запуск парсинга",
    `Найдено ${skuCount} SKU.\nНачать парсинг?`,
    ui.ButtonSet.YES_NO
  );

  if (response !== ui.Button.YES) {
    return;
  }

  // Отправляем запрос на API
  try {
    const payload = {
      spreadsheet_id: spreadsheetId,
      sheet_name: sheetName,
      column_sku: "A",
      start_row: 2
    };

    const options = {
      method: "POST",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };

    const response = UrlFetchApp.fetch(`${API_URL}/api/parse`, options);
    const result = JSON.parse(response.getContentText());

    if (result.task_id) {
      ui.alert(
        "Парсинг запущен!",
        `Task ID: ${result.task_id}\n\nРезультаты будут записываться в таблицу по мере парсинга.\n\nОжидаемое время: ~${Math.ceil(skuCount * 3 / 60)} мин`,
        ui.ButtonSet.OK
      );

      // Сохраняем task_id для проверки статуса
      PropertiesService.getScriptProperties().setProperty("lastTaskId", result.task_id);
    } else {
      ui.alert("Ошибка", `API вернул: ${JSON.stringify(result)}`, ui.ButtonSet.OK);
    }

  } catch (error) {
    ui.alert("Ошибка подключения", error.toString(), ui.ButtonSet.OK);
  }
}

/**
 * Проверка статуса парсинга
 */
function checkStatus() {
  const taskId = PropertiesService.getScriptProperties().getProperty("lastTaskId");

  if (!taskId) {
    SpreadsheetApp.getUi().alert("Нет активных задач");
    return;
  }

  try {
    const response = UrlFetchApp.fetch(`${API_URL}/api/parse/status/${taskId}`);
    const status = JSON.parse(response.getContentText());

    const message = `
      Статус: ${status.status}
      Прогресс: ${status.progress}
      Обработано: ${status.processed}/${status.total}
      Ошибок: ${status.errors}
    `;

    SpreadsheetApp.getUi().alert("Статус парсинга", message, SpreadsheetApp.getUi().ButtonSet.OK);

  } catch (error) {
    SpreadsheetApp.getUi().alert("Ошибка", error.toString(), SpreadsheetApp.getUi().ButtonSet.OK);
  }
}

/**
 * Записать заголовки колонок
 */
function writeHeaders() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Парсинг товаров");

  if (!sheet) {
    SpreadsheetApp.getUi().alert("Лист 'Парсинг товаров' не найден!");
    return;
  }

  const headers = [
    ["SKU", "Название", "Цена", "Бренд", "Рейтинг", "Отзывы", "Наличие", "Дата парсинга", "Ошибка"]
  ];

  sheet.getRange("A1:I1").setValues(headers);
  sheet.getRange("A1:I1").setFontWeight("bold");
  sheet.getRange("A1:I1").setBackground("#4285f4");
  sheet.getRange("A1:I1").setFontColor("#ffffff");

  // Ширина колонок
  sheet.setColumnWidth(1, 120);  // SKU
  sheet.setColumnWidth(2, 400);  // Название
  sheet.setColumnWidth(3, 80);   // Цена
  sheet.setColumnWidth(4, 150);  // Бренд
  sheet.setColumnWidth(5, 70);   // Рейтинг
  sheet.setColumnWidth(6, 80);   // Отзывы
  sheet.setColumnWidth(7, 100);  // Наличие
  sheet.setColumnWidth(8, 150);  // Дата
  sheet.setColumnWidth(9, 200);  // Ошибка

  SpreadsheetApp.getUi().alert("Заголовки добавлены!");
}

/**
 * Меню в таблице
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu("🔍 Ozon Parser")
    .addItem("▶️ Запустить парсинг", "parseOzon")
    .addItem("📊 Проверить статус", "checkStatus")
    .addSeparator()
    .addItem("📝 Добавить заголовки", "writeHeaders")
    .addToUi();
}
