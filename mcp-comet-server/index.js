#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { chromium } from 'playwright';

const server = new Server(
  {
    name: 'comet-browser',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Функция глубокого исследования через Comet
async function deepResearch(query, maxTime = 600000) {
  let browser;
  let context;

  try {
    console.error(`🚀 Запуск Comet Browser для: ${query}`);

    // Запуск Chromium (или можно подключиться к существующему Comet)
    browser = await chromium.launch({
      headless: false, // Показывать браузер
      channel: 'chrome' // Использовать установленный Chrome
    });

    context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    });

    const page = await context.newPage();

    // Открыть Perplexity Comet (веб-версия)
    console.error('📡 Подключение к Perplexity...');
    await page.goto('https://www.perplexity.ai/', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // Подождать загрузки страницы
    await page.waitForTimeout(3000);

    // Найти поле ввода и ввести запрос
    console.error('✏️ Ввод запроса...');
    const inputSelector = 'textarea, input[type="text"]';
    await page.waitForSelector(inputSelector, { timeout: 10000 });
    await page.fill(inputSelector, query);

    // Отправить запрос
    await page.keyboard.press('Enter');

    // Ждать начала исследования
    console.error('🔍 Ожидание результатов (может занять до 10 минут)...');
    await page.waitForTimeout(5000);

    // Ждать появления результатов
    // Perplexity показывает результаты в div с классом answer
    let resultText = '';
    let attempts = 0;
    const maxAttempts = Math.floor(maxTime / 5000);

    while (attempts < maxAttempts) {
      try {
        // Попытка извлечь текст ответа
        const answerElements = await page.$$('[class*="answer"], [class*="result"], [class*="response"]');

        if (answerElements.length > 0) {
          // Извлечь текст из всех элементов
          const texts = await Promise.all(
            answerElements.map(el => el.textContent())
          );
          resultText = texts.join('\n\n');

          if (resultText.length > 100) {
            console.error('✅ Результаты получены!');
            break;
          }
        }
      } catch (e) {
        // Продолжаем ждать
      }

      attempts++;
      await page.waitForTimeout(5000);
    }

    if (!resultText) {
      // Fallback: извлечь весь видимый текст
      resultText = await page.evaluate(() => document.body.innerText);
    }

    // Извлечь источники
    const sources = await page.$$eval('a[href^="http"]', links =>
      links.slice(0, 10).map(a => ({
        title: a.textContent.trim(),
        url: a.href
      }))
    );

    return {
      query,
      answer: resultText,
      sources,
      timestamp: new Date().toISOString()
    };

  } catch (error) {
    console.error('❌ Ошибка:', error.message);
    throw error;
  } finally {
    if (context) await context.close();
    if (browser) await browser.close();
  }
}

// Регистрация инструмента deep_research
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'deep_research',
        description: 'Проводит глубокое исследование темы через Perplexity Comet Browser (автоматизация). Использует браузер напрямую, обходя API лимиты. Может занять 5-15 минут.',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Тема для глубокого исследования'
            },
            max_time_seconds: {
              type: 'number',
              description: 'Максимальное время ожидания в секундах (по умолчанию 600 = 10 минут)',
              default: 600
            }
          },
          required: ['query']
        }
      }
    ]
  };
});

// Обработчик вызова инструмента
server.setRequestHandler('tools/call', async (request) => {
  if (request.params.name === 'deep_research') {
    const { query, max_time_seconds = 600 } = request.params.arguments;

    try {
      const result = await deepResearch(query, max_time_seconds * 1000);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Ошибка исследования: ${error.message}`
          }
        ],
        isError: true
      };
    }
  }

  throw new Error(`Неизвестный инструмент: ${request.params.name}`);
});

// Запуск сервера
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('🎯 MCP Comet Browser Server запущен');
}

main().catch(console.error);
