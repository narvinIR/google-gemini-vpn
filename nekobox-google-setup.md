# 🚀 Полная настройка NekoBox для обхода Google AI Studio

**Проблема:** Google AI Studio блокирует доступ из России  
**Причина:** Google детектит регион по языку браузера и истории аккаунта  
**Решение:** Комплексная настройка VPN + браузер + новый аккаунт

---

## 🔴 ГЛАВНАЯ ПРОБЛЕМА (из твоих данных ipleak.net)

```
Accept-Language: ru, en;q=0.9  ← ПАЛИТ РОССИЮ!
```

**Твой VPN работает нормально:**
- ✅ IP: 89.169.15.11 (Estonia) 
- ✅ DNS: Cloudflare (172.69.136.115)
- ❌ Язык браузера: РУССКИЙ на первом месте!

---

## 📝 План действий (в строгом порядке!)

### Шаг 1: Настройка NekoBox (DNS)

#### 1.1 Открой конфиг NekoBox
Файл: `%USERPROFILE%\.config\nekoray\config\routing.json`

#### 1.2 Добавь правила DNS
```json
{
  "dns": {
    "servers": [
      {
        "tag": "cloudflare-doh",
        "address": "https://1.1.1.1/dns-query",
        "address_resolver": "cloudflare-direct"
      },
      {
        "tag": "cloudflare-direct",
        "address": "1.1.1.1",
        "detour": "direct"
      }
    ],
    "rules": [
      {
        "outbound": "any",
        "server": "cloudflare-doh"
      }
    ],
    "strategy": "prefer_ipv4",
    "disable_cache": false,
    "disable_expire": false
  }
}
```

#### 1.3 В GUI NekoBox включи:
1. `Settings` → `Routing Settings`
2. ✅ `Hijack DNS` (перехват DNS)
3. ✅ `Fake DNS` 
4. Remote DNS: `https://1.1.1.1/dns-query`
5. Strategy: `prefer_ipv4`

---

### Шаг 2: Создай изолированный профиль Chrome

#### 2.1 Создай bat-файл для запуска
Файл: `C:\gemini-chrome.bat`

```batch
@echo off
REM Устанавливаем английскую локаль
set LANG=en_US.UTF-8
set LANGUAGE=en_US
set LC_ALL=en_US.UTF-8

REM Запускаем Chrome с изолированным профилем
"C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --user-data-dir="%USERPROFILE%\ChromeGemini" ^
  --lang=en-US ^
  --disable-features=WebRtcHideLocalIpsWithMdns ^
  --webrtc-ip-handling-policy=disable_non_proxied_udp ^
  --disable-web-security ^
  --disable-site-isolation-trials
  
pause
```

#### 2.2 Запусти bat-файл
Двойной клик на `gemini-chrome.bat` → откроется новый Chrome

---

### Шаг 3: Настройка нового профиля Chrome

#### 3.1 В новом Chrome зайди в настройки
`chrome://settings/languages`

**КРИТИЧЕСКИ ВАЖНО:**
1. Удали русский язык полностью
2. Добавь только English (United States)
3. Перезапусти Chrome

#### 3.2 Настройки региона
`chrome://settings/`
- Region: `Estonia` или `United States`
- Time zone: `Tallinn` или `New York`

#### 3.3 Очисти всё
`chrome://settings/clearBrowserData`
- ✅ Cookies
- ✅ Cached images
- ✅ Site settings
- Time range: `All time`

---

### Шаг 4: Проверка утечек

#### 4.1 Проверь ipleak.net
Зайди на https://ipleak.net и проверь:

```
✅ IP: Estonia (не Россия)
✅ DNS: Cloudflare (не российские провайдеры)  
✅ Accept-Language: en-US, en;q=0.9 (БЕЗ "ru"!)
✅ WebRTC: No leaks
```

#### 4.2 Проверь dnsleaktest.com
https://dnsleaktest.com → Extended Test

**Должны быть ТОЛЬКО:**
- Cloudflare servers
- Estonia или USA
- НИКАКИХ российских DNS!

#### 4.3 Проверь browserleaks.com
https://browserleaks.com/geo

```
✅ Geolocation API: Estonia
✅ Timezone: Europe/Tallinn (UTC+2)
✅ Language: en-US
```

---

### Шаг 5: Создай НОВЫЙ Google аккаунт

**ОБЯЗАТЕЛЬНО через VPN и настроенный Chrome!**

#### 5.1 Подготовка
1. ✅ NekoBox включен
2. ✅ Chrome запущен через bat-файл
3. ✅ Проверил ipleak.net (всё чисто)
4. ✅ Режим инкогнито в Chrome

#### 5.2 Создание аккаунта
1. Зайди на https://accounts.google.com/signup
2. **НЕ используй российский номер телефона!**
3. Варианты:
   - Купи виртуальный номер (onlinesim.io - Эстония)
   - Используй email для восстановления (proton.me)
   - Пропусти номер телефона (иногда можно)

#### 5.3 При регистрации укажи:
- Country: `Estonia` (или регион твоего VPN)
- Language: `English (United States)`
- Timezone: `Tallinn`

#### 5.4 После создания
1. Зайди в https://myaccount.google.com/language
2. Убедись что везде English
3. НЕ добавляй русский язык!

---

### Шаг 6: Первый вход в Google AI Studio

#### 6.1 Подготовка
1. ✅ VPN включен
2. ✅ Chrome с новым профилем
3. ✅ Новый Google аккаунт
4. ✅ Режим инкогнито

#### 6.2 Заход в AI Studio
1. Открой https://aistudio.google.com
2. Войди НОВЫМ аккаунтом
3. Если просит регион → выбери Estonia

#### 6.3 Если всё ок:
```
✅ Откроется интерфейс AI Studio
✅ Доступны все модели (gemini-2.5-pro и т.д.)
✅ Можно создавать API ключи
```

---

## 🔧 Дополнительные настройки NekoBox

### Оптимизация для Google

#### В конфиге routing добавь:
```json
{
  "routing": {
    "rules": [
      {
        "domain_suffix": [
          "google.com",
          "googleapis.com",
          "gstatic.com",
          "googleusercontent.com"
        ],
        "outbound": "proxy"
      }
    ]
  }
}
```

### Проверка работы VPN
```bash
# В PowerShell
nslookup google.com

# Должен показать:
# Server: 1.1.1.1 (Cloudflare)
# Address: 89.169.15.11 (твой VPN IP)
```

---

## 🚨 Частые ошибки

### ❌ "This service is not available in your region"

**Причины:**
1. Язык браузера всё ещё русский
2. Используешь старый Google аккаунт
3. DNS утечка
4. История браузера не очищена

**Решение:**
1. Проверь ipleak.net → Accept-Language должен быть en-US
2. Создай новый аккаунт
3. Очисти все данные Chrome
4. Перезапусти NekoBox

### ❌ DNS утечки

**Проверка:**
```bash
# PowerShell
ipconfig /all | findstr DNS

# Должно быть: 1.1.1.1 или 1.0.0.1
# НЕ должно быть: 192.168.x.x, провайдерские DNS
```

**Фикс:**
```bash
# Очисти DNS кеш
ipconfig /flushdns

# Перезапусти NekoBox
```

### ❌ WebRTC утечки

**Установи расширение:**
- Chrome: [WebRTC Leak Shield](https://chrome.google.com/webstore/detail/webrtc-leak-shield)
- Или встроенное в bat-файле уже отключает

---

## 🎯 Финальный чеклист

Перед заходом в Google AI Studio:

```
☐ NekoBox запущен и работает
☐ Chrome запущен через bat-файл (изолированный профиль)
☐ ipleak.net показывает:
  ☐ IP: Estonia
  ☐ DNS: Cloudflare
  ☐ Language: en-US (БЕЗ ru!)
☐ dnsleaktest.com: только Cloudflare
☐ Новый Google аккаунт создан через VPN
☐ Аккаунт настроен на English + Estonia
☐ Все cookies очищены
```

---

## 💡 Альтернативные решения

### Вариант 1: Cloudflare WARP
Часто обходит блокировки Google лучше обычных VPN:

1. Скачай: https://1.1.1.1/
2. Установи WARP
3. Выбери режим "WARP" (не WARP+)
4. Попробуй зайти в AI Studio

### Вариант 2: Double VPN
```
NekoBox → Cloudflare WARP → Google
```

Запусти оба одновременно для двойного туннелирования.

### Вариант 3: Residential Proxy
Если VPN не помогает:
- Mysterium VPN (децентрализованные ноды)
- IPRoyal Residential
- Bright Data (дорого, но стабильно)

---

## 📞 Тестирование

### После всех настроек проверь:

1. **ipleak.net**
```
IP: 89.169.15.11 (Estonia) ✓
DNS: Cloudflare ✓
Language: en-US ✓
```

2. **Google AI Studio**
```bash
# Должно открыться без ошибок
https://aistudio.google.com
```

3. **API тест**
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

---

## 🔗 Полезные ссылки

- NekoBox: https://github.com/MatsuriDayo/nekoray
- Cloudflare WARP: https://1.1.1.1/
- DNS Leak Test: https://dnsleaktest.com
- IP Leak: https://ipleak.net
- Browser Leaks: https://browserleaks.com

---

**Главное правило:** Google детектит регион по **языку браузера** в первую очередь! Язык должен быть ТОЛЬКО английский.

Если после всех настроек не работает → пиши, разберём дальше!
