#!/usr/bin/env node
/**
 * MCP Comet Browser Server
 * Автоматизация Perplexity Pro через браузер
 * Поддерживает ВСЕ модели: GPT-5.1, Claude, Gemini, Grok, Sonar
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { chromium } from 'playwright';
import path from 'path';
import os from 'os';

// Конфигурация моделей Perplexity Pro
const MODELS = {
  'sonar': { name: 'Sonar Pro', selector: null }, // По умолчанию
  'gpt-5.1': { name: 'GPT-5.1', selector: 'GPT-5.1' },
  'claude': { name: 'Claude 4 Sonnet', selector: 'Claude' },
  'gemini': { name: 'Gemini 2.5 Pro', selector: 'Gemini' },
  'grok': { name: 'Grok 3', selector: 'Grok' }
};

const server = new Server(
  {
    name: 'comet-browser',
    version: '2.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Путь к профилю браузера (сохраняет логин в Perplexity)
const BROWSER_PROFILE = path.join(os.homedir(), 'PerplexityCometProfile');

// Основная функция запроса к Perplexity
async function askPerplexity(query, model = 'sonar', maxWaitMs = 120000) {
  let browser;
  let context;

  try {
    console.error(`🚀 Perplexity ${MODELS[model]?.name || model}: ${query.substring(0, 50)}...`);

    // Запуск браузера с сохранённым профилем
    context = await chromium.launchPersistentContext(BROWSER_PROFILE, {
      headless: false,
      channel: 'chrome',
      viewport: { width: 1400, height: 900 },
      locale: 'en-US'
    });

    const page = context.pages()[0] || await context.newPage();

    // Переход на Perplexity
    console.error('📡 Подключение к Perplexity...');
    await page.goto('https://www.perplexity.ai/', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    await page.waitForTimeout(2000);

    // Выбор модели (если не sonar)
    if (model !== 'sonar' && MODELS[model]) {
      console.error(`🔄 Выбор модели: ${MODELS[model].name}`);
      try {
        // Клик на селектор модели
        const modelButton = await page.$('[data-testid="model-selector"], button:has-text("Sonar"), button:has-text("Pro")');
        if (modelButton) {
          await modelButton.click();
          await page.waitForTimeout(500);

          // Выбор нужной модели
          const modelOption = await page.$(`text=${MODELS[model].selector}`);
          if (modelOption) {
            await modelOption.click();
            await page.waitForTimeout(500);
          }
        }
      } catch (e) {
        console.error(`⚠️ Не удалось выбрать модель: ${e.message}`);
      }
    }

    // Ввод запроса
    console.error('✏️ Ввод запроса...');
    const inputSelector = 'textarea[placeholder*="Ask"], textarea, input[type="text"]';
    await page.waitForSelector(inputSelector, { timeout: 10000 });

    // Очистка и ввод
    await page.click(inputSelector);
    await page.fill(inputSelector, query);
    await page.waitForTimeout(300);

    // Отправка
    await page.keyboard.press('Enter');
    console.error('🔍 Ожидание ответа...');

    // Ждём появления ответа
    let resultText = '';
    let attempts = 0;
    const maxAttempts = Math.floor(maxWaitMs / 3000);

    while (attempts < maxAttempts) {
      await page.waitForTimeout(3000);
      attempts++;

      try {
        // Извлечение ответа (несколько селекторов)
        const answerSelectors = [
          '[class*="prose"]',
          '[class*="answer"]',
          '[class*="response"]',
          '[class*="markdown"]',
          'article',
          '.text-base'
        ];

        for (const sel of answerSelectors) {
          const elements = await page.$$(sel);
          if (elements.length > 0) {
            const texts = await Promise.all(elements.map(el => el.textContent()));
            const combined = texts.join('\n').trim();
            if (combined.length > resultText.length) {
              resultText = combined;
            }
          }
        }

        // Проверяем что ответ полный (нет индикатора загрузки)
        const isLoading = await page.$('[class*="loading"], [class*="typing"], .animate-pulse');
        if (!isLoading && resultText.length > 100) {
          console.error('✅ Ответ получен!');
          break;
        }

      } catch (e) {
        // Продолжаем ждать
      }
    }

    // Извлечение источников
    let sources = [];
    try {
      sources = await page.$$eval('a[href^="http"]:not([href*="perplexity"])', links =>
        links.slice(0, 10).map(a => ({
          title: a.textContent?.trim().substring(0, 100) || '',
          url: a.href
        })).filter(s => s.title && s.url)
      );
    } catch (e) { }

    // Не закрываем браузер - оставляем профиль для следующих запросов
    // await context.close();

    return {
      model: MODELS[model]?.name || model,
      query,
      answer: resultText || 'Ответ не получен. Возможно нужен логин в Perplexity Pro.',
      sources,
      timestamp: new Date().toISOString()
    };

  } catch (error) {
    console.error('❌ Ошибка:', error.message);
    if (context) await context.close();
    throw error;
  }
}

// Deep Research (длительное исследование)
async function deepResearch(query, maxTimeMs = 900000) {
  let context;

  try {
    console.error(`🔬 Deep Research: ${query.substring(0, 50)}...`);

    context = await chromium.launchPersistentContext(BROWSER_PROFILE, {
      headless: false,
      channel: 'chrome',
      viewport: { width: 1400, height: 900 }
    });

    const page = context.pages()[0] || await context.newPage();

    // Переход на страницу Deep Research
    await page.goto('https://www.perplexity.ai/', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);

    // Активация режима Deep Research
    console.error('🔄 Активация Deep Research...');
    try {
      const deepButton = await page.$('button:has-text("Deep"), button:has-text("Research"), [data-testid="deep-research"]');
      if (deepButton) {
        await deepButton.click();
        await page.waitForTimeout(1000);
      }
    } catch (e) {
      console.error('⚠️ Deep Research кнопка не найдена, используем обычный режим');
    }

    // Ввод запроса
    const inputSelector = 'textarea, input[type="text"]';
    await page.waitForSelector(inputSelector);
    await page.fill(inputSelector, query);
    await page.keyboard.press('Enter');

    console.error('🔍 Deep Research начат (может занять 5-15 минут)...');

    // Длительное ожидание
    let resultText = '';
    let attempts = 0;
    const maxAttempts = Math.floor(maxTimeMs / 10000);

    while (attempts < maxAttempts) {
      await page.waitForTimeout(10000);
      attempts++;

      // Проверка прогресса
      const progress = await page.$('[class*="progress"], [class*="status"]');
      if (progress) {
        const status = await progress.textContent();
        console.error(`   Прогресс: ${status}`);
      }

      // Извлечение результата
      const elements = await page.$$('[class*="prose"], [class*="answer"], article');
      if (elements.length > 0) {
        const texts = await Promise.all(elements.map(el => el.textContent()));
        resultText = texts.join('\n').trim();
      }

      // Проверка завершения
      const isComplete = await page.$('text=Complete, text=Done, text=Finished');
      if (isComplete && resultText.length > 500) {
        console.error('✅ Deep Research завершён!');
        break;
      }
    }

    return {
      type: 'deep_research',
      query,
      answer: resultText || 'Deep Research не завершился за отведённое время',
      timestamp: new Date().toISOString()
    };

  } catch (error) {
    console.error('❌ Ошибка:', error.message);
    if (context) await context.close();
    throw error;
  }
}

// Регистрация инструментов
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'perplexity_ask',
        description: 'Задать вопрос Perplexity Pro через браузер. Поддерживает модели: sonar (default), gpt-5.1, claude, gemini, grok',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'Вопрос или запрос' },
            model: {
              type: 'string',
              enum: ['sonar', 'gpt-5.1', 'claude', 'gemini', 'grok'],
              description: 'Модель для использования (по умолчанию sonar)',
              default: 'sonar'
            }
          },
          required: ['query']
        }
      },
      {
        name: 'perplexity_gpt5',
        description: 'Запрос к GPT-5.1 через Perplexity Pro',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'Вопрос для GPT-5.1' }
          },
          required: ['query']
        }
      },
      {
        name: 'perplexity_claude',
        description: 'Запрос к Claude 4 через Perplexity Pro',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'Вопрос для Claude' }
          },
          required: ['query']
        }
      },
      {
        name: 'perplexity_gemini',
        description: 'Запрос к Gemini 2.5 Pro через Perplexity Pro',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'Вопрос для Gemini' }
          },
          required: ['query']
        }
      },
      {
        name: 'perplexity_grok',
        description: 'Запрос к Grok 3 через Perplexity Pro',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'Вопрос для Grok' }
          },
          required: ['query']
        }
      },
      {
        name: 'deep_research',
        description: 'Глубокое исследование через Perplexity Deep Research. Занимает 5-15 минут, но даёт исчерпывающий ответ.',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'Тема для глубокого исследования' },
            max_time_minutes: {
              type: 'number',
              description: 'Максимальное время (минуты)',
              default: 15
            }
          },
          required: ['query']
        }
      }
    ]
  };
});

// Обработчик вызовов
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result;

    switch (name) {
      case 'perplexity_ask':
        result = await askPerplexity(args.query, args.model || 'sonar');
        break;
      case 'perplexity_gpt5':
        result = await askPerplexity(args.query, 'gpt-5.1');
        break;
      case 'perplexity_claude':
        result = await askPerplexity(args.query, 'claude');
        break;
      case 'perplexity_gemini':
        result = await askPerplexity(args.query, 'gemini');
        break;
      case 'perplexity_grok':
        result = await askPerplexity(args.query, 'grok');
        break;
      case 'deep_research':
        result = await deepResearch(args.query, (args.max_time_minutes || 15) * 60000);
        break;
      default:
        throw new Error(`Неизвестный инструмент: ${name}`);
    }

    return {
      content: [{
        type: 'text',
        text: JSON.stringify(result, null, 2)
      }]
    };

  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: `Ошибка: ${error.message}`
      }],
      isError: true
    };
  }
});

// Запуск
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('🎯 MCP Comet Browser Server v2.0 запущен');
  console.error('   Модели: GPT-5.1, Claude, Gemini, Grok, Sonar');
  console.error(`   Профиль: ${BROWSER_PROFILE}`);
}

main().catch(console.error);
