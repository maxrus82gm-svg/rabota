# ULTRA TASK — FINAL CONTROLLED BUILD
# GigaCodexBridge Home Setup v1.0

РОЛЬ

Ты не проектировщик и не архитектор этой задачи.

Ты являешься ИСПОЛНИТЕЛЕМ по жёсткой технической спецификации.

Все архитектурные решения уже приняты и проверены человеком.

Тебе ЗАПРЕЩЕНО:
- предлагать альтернативную архитектуру;
- менять OAuth flow;
- менять MCP framework;
- менять рабочий server.py по своему усмотрению;
- заменять зависимости аналогами;
- использовать Cursor/Windsurf вместо Codex;
- додумывать неизвестные детали;
- упрощать обязательные проверки;
- сохранять Authorization Key в файлы;
- выводить access_token;
- отключать SSL verification как постоянное решение.

Если требование ниже кажется тебе необычным —
всё равно исполняй его буквально.

==================================================
ЦЕЛЬ
==================================================

Нужно создать ОДИН PowerShell-файл:

02_BUILD_PACKAGE.ps1

Он будет сохранён bridge-инструментом автоматически.

Этот файл НЕ устанавливает GigaCodexBridge.

Его единственная задача:

создать рядом с собой готовую переносную папку:

GigaCodexBridge_Home_Setup_v1.0

с файлами:

GigaCodexBridge_Home_Setup_v1.0\
    install.bat
    install.ps1
    server.py
    README.md

Также допускается:

GigaCodexBridge_Home_Setup_v1.0\
    BUILD_INFO.md

если он нужен для краткого описания состава пакета.

НИКАКИХ ДРУГИХ ФАЙЛОВ НЕ СОЗДАВАТЬ.

02_BUILD_PACKAGE.ps1 должен создавать пакет в:

Join-Path $PSScriptRoot "GigaCodexBridge_Home_Setup_v1.0"

Он НЕ должен:
- менять Windows;
- устанавливать Python;
- менять config.toml;
- писать переменные среды;
- скачивать файлы;
- обращаться в интернет;
- запускать install.bat;
- запускать install.ps1.

Он только создаёт текстовые файлы переносного комплекта.

==================================================
ФОРМАТ ТВОЕГО ОТВЕТА
==================================================

КРИТИЧЕСКИ ВАЖНО.

Твой ответ будет напрямую сохранён как:

02_BUILD_PACKAGE.ps1

Поэтому ответ должен содержать ТОЛЬКО валидный PowerShell-код.

НЕ использовать markdown fences.

НЕ писать:

```powershell

НЕ писать пояснения до кода.

НЕ писать пояснения после кода.

НЕ писать отчёт обычным текстом.

Первая строка ответа должна быть PowerShell-кодом.

Последняя строка ответа должна быть PowerShell-кодом.

==================================================
АРХИТЕКТУРА УСТАНАВЛИВАЕМОЙ СИСТЕМЫ
==================================================

После запуска install.bat на домашнем Windows-компьютере
рабочая установка должна размещаться в:

%LOCALAPPDATA%\GigaCodexBridge

То есть примерно:

C:\Users\<USER>\AppData\Local\GigaCodexBridge

В ней должны быть:

server.py
russian_trusted_root_ca_pem.crt
.venv\
logs\

Переносной пакет и установленный bridge —
это разные вещи.

==================================================
PYTHON
==================================================

Требуется:

Python 3.12

На компьютере могут существовать другие версии Python,
например Python 3.9 от Visual Studio.

НЕЛЬЗЯ определять нужную версию только через:

python --version

Приоритетная проверка:

py -3.12

Если Python 3.12 отсутствует,
install.ps1 должен проверить наличие winget.

При наличии winget разрешена установка:

winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements

После установки нужно повторно найти Python 3.12.

Допускается дополнительно искать:

%LOCALAPPDATA%\Programs\Python\Python312\python.exe

и другие стандартные пути Python 3.12.

Другие версии Python НЕ удалять и НЕ менять.

==================================================
VENV
==================================================

Virtual environment:

%LOCALAPPDATA%\GigaCodexBridge\.venv

Создание:

Python 3.12 -m venv <VenvDir>

Проверенный путь Python внутри Windows venv:

.venv\Scripts\python.exe

НЕ использовать:

.venv\python.exe

Для дальнейших действий использовать именно:

<VenvDir>\Scripts\python.exe

Не полагаться на активированный venv.

==================================================
ЗАВИСИМОСТИ
==================================================

Устанавливать ТОЛЬКО:

mcp[cli]
httpx
certifi

Рабочая логика:

<VenvPython> -m pip install --upgrade pip

<VenvPython> -m pip install "mcp[cli]" httpx certifi

НЕ использовать:

mcp-sdk-python
requests
python-dotenv

если они не являются транзитивными зависимостями,
устанавливаемыми pip автоматически.

==================================================
GIGACHAT AUTH
==================================================

Постоянный Authorization Key:

GIGACHAT_CREDENTIALS

Scope:

GIGACHAT_SCOPE=GIGACHAT_API_PERS


ПРАВИЛЬНЫЙ FLOW:

1.

POST

https://ngw.devices.sberbank.ru:9443/api/v2/oauth

Authorization:

Basic <GIGACHAT_CREDENTIALS>

Content-Type:

application/x-www-form-urlencoded

RqUID:

UUID

Body:

scope=GIGACHAT_API_PERS


2.

Получить:

access_token


3.

Только временный access_token использовать как:

Authorization: Bearer <access_token>

для:

https://api.giga.chat/v1/chat/completions


Authorization Key НИКОГДА не использовать как Bearer.

access_token НИКОГДА не показывать пользователю.

==================================================
ХРАНЕНИЕ СЕКРЕТА
==================================================

install.ps1 должен запросить Authorization Key интерактивно.

Желательно использовать:

Read-Host -AsSecureString

Разрешено временно преобразовать SecureString в обычную строку
ТОЛЬКО в памяти процесса,
если это требуется для записи User Environment Variable.

Сохранить:

GIGACHAT_CREDENTIALS

как Windows User Environment Variable.

Сохранить:

GIGACHAT_SCOPE=GIGACHAT_API_PERS

как Windows User Environment Variable.

Использовать:

[System.Environment]::SetEnvironmentVariable(..., "User")

или эквивалентный корректный .NET-вызов.

Также установить эти две переменные в:

$env:

текущего installer-процесса,
чтобы выполнить тесты без перезапуска PowerShell.

ЗАПРЕЩЕНО сохранять Authorization Key:

- в server.py;
- в install.ps1;
- в install.bat;
- в README.md;
- в config.toml;
- в BUILD_INFO.md;
- в логах.

==================================================
SSL / CERTIFI
==================================================

На реальной машине уже была получена ошибка:

CERTIFICATE_VERIFY_FAILED
self-signed certificate in certificate chain

Рабочее решение уже проверено.

Используется:

https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt

Файл сохранить как:

%LOCALAPPDATA%\GigaCodexBridge\russian_trusted_root_ca_pem.crt


Сначала попытаться скачать обычным безопасным способом.

Если Windows PowerShell не может скачать сертификат
именно из-за bootstrap-проблемы доверия,
допускается fallback:

curl.exe -k

ТОЛЬКО для скачивания этого конкретного сертификата
с указанного выше фиксированного URL.

Это не означает отключение SSL для GigaChat API.


После установки certifi определить реальный CA bundle через:

<VenvPython> -m certifi


КРИТИЧЕСКИ ВАЖНО:

НЕ заменять cacert.pem сертификатом НУЦ.

Нужно ДОБАВИТЬ PEM в существующий cacert.pem.

Повторный запуск install.ps1 должен быть идемпотентным.

Перед добавлением сравнить содержимое сертификата
с содержимым существующего bundle.

Если тот же сертификат уже присутствует —
повторно его не добавлять.

==================================================
SERVER.PY
==================================================

server.py в создаваемом переносном комплекте должен быть
основан СТРОГО на приведённом ниже проверенном baseline.

Не переизобретать его.

Не добавлять dotenv.

Не добавлять token cache на диск.

Не писать access_token на диск.

Не писать диагностические print() в stdout,
потому что stdout используется MCP stdio transport.

Можно исправить только очевидную синтаксическую ошибку,
если она существует,
но архитектуру и API не менять.

----- BEGIN VERIFIED SERVER.PY -----

import os
import time
import uuid
from pathlib import Path

import httpx
from mcp.server.mcpserver import MCPServer


mcp = MCPServer("GigaChat Ultra Subagent")

OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://api.giga.chat/v1/chat/completions"

MODEL = "GigaChat-3-Ultra"
TEMPERATURE = 0.15
MAX_TOKENS = 4096

MAX_TASK_FILE_BYTES = 2 * 1024 * 1024
ALLOWED_TEXT_SUFFIXES = {".md", ".txt"}

_access_token: str | None = None
_access_token_valid_until = 0.0


async def get_access_token() -> str:
    global _access_token, _access_token_valid_until

    if _access_token and time.time() < _access_token_valid_until:
        return _access_token

    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

    if not credentials:
        raise RuntimeError(
            "Не найдена переменная среды GIGACHAT_CREDENTIALS."
        )

    headers = {
        "Authorization": f"Basic {credentials}",
        "RqUID": str(uuid.uuid4()),
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            OAUTH_URL,
            headers=headers,
            data={"scope": scope},
        )
        response.raise_for_status()

    data = response.json()
    token = data.get("access_token")

    if not token:
        raise RuntimeError(
            f"GigaChat не вернул access_token: {data}"
        )

    _access_token = token
    _access_token_valid_until = time.time() + 25 * 60
    return token


async def ask_gigachat(prompt: str) -> str:
    token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(
            CHAT_URL,
            headers=headers,
            json=body,
        )
        response.raise_for_status()

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(
            f"Неожиданный ответ GigaChat: {data}"
        ) from exc


def _validate_text_file(path_text: str, *, must_exist: bool) -> Path:
    path = Path(path_text).expanduser()

    if not path.is_absolute():
        raise ValueError(
            "Путь должен быть абсолютным, например "
            r"D:\GitHub\rabota\Ultra\01_ULTRA_TASK.md"
        )

    if path.suffix.lower() not in ALLOWED_TEXT_SUFFIXES:
        raise ValueError(
            "Разрешены только текстовые файлы .md и .txt."
        )

    if must_exist:
        if not path.is_file():
            raise FileNotFoundError(f"Файл задачи не найден: {path}")

        size = path.stat().st_size
        if size > MAX_TASK_FILE_BYTES:
            raise ValueError(
                f"Файл задачи слишком большой: {size} байт. "
                f"Лимит: {MAX_TASK_FILE_BYTES} байт."
            )

    return path


@mcp.tool()
async def gigachat_ask(prompt: str) -> str:
    """
    Передай текстовую задачу GigaChat 3 Ultra как независимому субагенту.

    Используй для анализа, планирования, второй точки зрения,
    проверки кода, поиска ошибок и альтернативных решений.
    """
    return await ask_gigachat(prompt)


@mcp.tool()
async def gigachat_file_task(task_file: str, report_file: str) -> str:
    """
    Выполни большую задачу через GigaChat Ultra почти без расхода контекста Codex.

    Инструмент сам:
    1. читает task_file с локального диска;
    2. отправляет его содержимое GigaChat Ultra;
    3. получает полный ответ;
    4. записывает ответ в report_file;
    5. возвращает Codex только короткий статус.

    Оба пути должны быть абсолютными.
    Разрешены .md и .txt.
    """

    task_path = _validate_text_file(task_file, must_exist=True)
    report_path = _validate_text_file(report_file, must_exist=False)

    if task_path.parent.resolve() != report_path.parent.resolve():
        raise ValueError(
            "Для безопасности task_file и report_file должны "
            "находиться в одной папке."
        )

    task_text = task_path.read_text(encoding="utf-8-sig")

    if not task_text.strip():
        raise ValueError("Файл задачи пуст.")

    prompt = (
        "Ты работаешь как самостоятельный инженерный субагент.\n"
        "Ниже находится полное техническое задание из локального файла.\n"
        "Выполни его самостоятельно и подготовь содержательный итоговый отчёт.\n"
        "Не обращайся к Codex за дополнительными рассуждениями, если задача "
        "уже содержит достаточный контекст.\n"
        "Ответ должен быть пригоден для прямой записи в Markdown-файл отчёта.\n\n"
        "===== НАЧАЛО ЗАДАЧИ =====\n"
        f"{task_text}\n"
        "===== КОНЕЦ ЗАДАЧИ =====\n"
    )

    result = await ask_gigachat(prompt)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(result, encoding="utf-8")

    return (
        "Готово. GigaChat Ultra прочитал файл задачи и записал полный отчёт: "
        f"{report_path}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")

----- END VERIFIED SERVER.PY -----

ВАЖНО:

В создаваемом server.py текст docstring можно оставить как есть.

Не добавлять print() в stdout.

==================================================
ВАЖНОЕ ОГРАНИЧЕНИЕ ТЕКУЩЕГО gigachat_file_task
==================================================

В текущем baseline:

gigachat_file_task

разрешает report_file только:

.md
.txt

Однако текущая специальная задача использует bridge,
который может быть временно настроен человеком для сохранения
твоего ответа как 02_BUILD_PACKAGE.ps1.

НЕ пытайся решать это внутри создаваемого домашнего server.py.

Домашний server.py должен оставаться baseline выше
с разрешением только .md/.txt.

==================================================
CODEX CONFIG
==================================================

Файл:

%USERPROFILE%\.codex\config.toml

Существующий файл нельзя уничтожать.

Если файл существует —
перед изменением обязательно сделать timestamp backup.

Если директория:

%USERPROFILE%\.codex

не существует —
создать её.

Нужно создать или ПОЛНОСТЬЮ заменить только секцию:

[mcp_servers.gigachat_ultra]

Не создавать дубликаты.


Формат должен соответствовать этой структуре:

[mcp_servers.gigachat_ultra]
command = '<ABSOLUTE_PATH_TO>\.venv\Scripts\python.exe'
args = ['-u', '<ABSOLUTE_PATH_TO>\server.py']
cwd = '<ABSOLUTE_PATH_TO>'
enabled = true
env_vars = ["GIGACHAT_CREDENTIALS", "GIGACHAT_SCOPE"]
startup_timeout_sec = 30
tool_timeout_sec = 180

Можно также добавить:

enabled_tools = ["gigachat_ask", "gigachat_file_task"]

если используемая версия Codex принимает этот параметр.

НЕ помещать Authorization Key в:

env = {...}

НЕ помещать значение ключа напрямую в config.toml.

Использовать:

env_vars

для передачи уже существующих Windows User Environment Variables.

Для Windows-путей в TOML предпочтительно использовать
literal strings в одинарных кавычках,
чтобы не требовать двойного escaping backslash.

==================================================
БЕЗОПАСНОЕ ОБНОВЛЕНИЕ CONFIG.TOML
==================================================

Не заменять весь config.toml.

Алгоритм:

1. Прочитать существующий текст.
2. Найти точную секцию:

[mcp_servers.gigachat_ultra]

3. Если она существует —
удалить только её содержимое до следующего TOML section header.
4. Остальные секции сохранить без изменений.
5. Вставить одну новую актуальную секцию.
6. Перед записью обязательно создать backup.

Если безопасно заменить только одну секцию не получается —
installer должен остановиться с понятной ошибкой,
а не уничтожать config.toml.

==================================================
INSTALL.PS1 — ОБЯЗАТЕЛЬНЫЙ ПОРЯДОК
==================================================

install.ps1 должен:

1. Определить собственную директорию через $PSScriptRoot.

2. Определить:

$TargetDir =
Join-Path $env:LOCALAPPDATA "GigaCodexBridge"

3. Создать TargetDir и logs.

4. Найти Python 3.12.

5. При отсутствии установить Python 3.12 через winget,
если winget доступен.

6. Повторно найти Python 3.12.

7. При невозможности найти Python 3.12 —
остановиться с ненулевым exit code.

8. Скопировать packaged server.py из директории install.ps1 в TargetDir.

9. Создать или обновить:

$TargetDir\.venv

10. Использовать:

$TargetDir\.venv\Scripts\python.exe

11. Установить:

mcp[cli]
httpx
certifi

12. Скачать сертификат НУЦ.

13. Определить certifi bundle командой:

<VenvPython> -m certifi

14. Идемпотентно добавить сертификат в CA bundle.

15. Запросить Authorization Key.

16. Сохранить его как Windows USER environment variable.

17. Сохранить GIGACHAT_SCOPE.

18. Установить обе переменные также в текущий $env:.

19. Выполнить:

python -m py_compile server.py

20. Выполнить реальный OAuth test,
НЕ выводя access_token.

21. Выполнить реальный Chat API test.

Тестовый prompt:

Ответь строго одной строкой: OK

Не требовать буквально ответа OK для признания транспортного успеха:
достаточно успешного HTTP-ответа и непустого message.content.

22. Выполнить IN-PROCESS MCP tools/list.

Ожидаемый набор:

gigachat_ask
gigachat_file_task

Если одного инструмента нет —
установка считается FAILED.

23. Выполнить настоящий STDIO MCP tools/list
через:

mcp.Client
StdioServerParameters

и:

<VenvDir>\Scripts\python.exe
-u
<TargetDir>\server.py

Ожидаемый набор:

gigachat_ask
gigachat_file_task

Если stdio tools/list не проходит —
установка считается FAILED.

24. Только после успешных технических тестов
обновить config.toml Codex.

25. Сообщить:

INSTALLATION SUCCESSFUL

26. Напомнить:

полностью закрыть Codex,
убедиться что процесс Codex завершён,
и открыть Codex заново.

==================================================
MCP SELF TEST
==================================================

Для self-test можно временно создать Python-файл
в TargetDir или logs.

Он должен использовать реально установленный пакет mcp.

IN-PROCESS тест должен быть эквивалентен:

from mcp import Client
from server import mcp

async with Client(mcp) as client:
    tools = await client.list_tools()

Проверить имена tools.


STDIO тест должен быть эквивалентен:

from mcp import Client, StdioServerParameters

params = StdioServerParameters(
    command=<VenvPython>,
    args=["-u", <ServerPath>],
    env={
        "GIGACHAT_CREDENTIALS": os.environ["GIGACHAT_CREDENTIALS"],
        "GIGACHAT_SCOPE": os.environ.get(
            "GIGACHAT_SCOPE",
            "GIGACHAT_API_PERS"
        ),
    },
)

async with Client(params) as client:
    tools = await client.list_tools()


После теста временный файл можно удалить.

==================================================
ЛОГИ
==================================================

Допускается лог:

%LOCALAPPDATA%\GigaCodexBridge\logs\install_<timestamp>.log

В лог разрешено писать:

- этап установки;
- версия Python;
- успех/ошибка pip;
- успех/ошибка SSL;
- OAuth OK / FAILED;
- Chat API OK / FAILED;
- список MCP tool names;
- путь backup config;
- итоговый статус.

В лог ЗАПРЕЩЕНО писать:

- Authorization Key;
- Basic Authorization header;
- access_token;
- Bearer header;
- полный API response, если в нём может быть token.

==================================================
INSTALL.BAT
==================================================

install.bat должен:

- работать из любой директории;
- использовать %~dp0;
- включить UTF-8 консоль через chcp 65001;
- вызвать соседний install.ps1;
- использовать:

powershell.exe -NoProfile -ExecutionPolicy Bypass

- корректно вернуть ERRORLEVEL;
- показать SUCCESS или FAILED;
- сделать pause в конце,
чтобы пользователь видел результат.

install.bat НЕ должен содержать никакие секреты.

==================================================
README.MD
==================================================

README должен быть на русском языке.

Это инструкция именно для:

Codex

НЕ писать, что основной продукт —
Cursor или Windsurf.

README должен объяснять очень коротко:

1. Полностью закрыть Codex.
2. Запустить install.bat.
3. Вставить Authorization Key.
4. Дождаться всех зелёных/успешных проверок.
5. Полностью перезапустить Codex.
6. Проверить gigachat_ask.
7. Проверить gigachat_file_task.

Отдельно объяснить:

Authorization Key != access_token.

Authorization Key постоянный и хранится
как User Environment Variable Windows.

access_token получает bridge автоматически.

README не должен содержать реальный ключ.

==================================================
ПОВТОРНЫЙ ЗАПУСК INSTALLER
==================================================

Повторный запуск обязан быть безопасным.

Он не должен:

- дублировать сертификат;
- дублировать MCP-секцию;
- удалять другие секции config.toml;
- ломать существующую .venv;
- удалять другие Python;
- выводить старый Authorization Key.

Допускается обновить зависимости pip.

Допускается заменить установленный server.py
на новую копию из переносного пакета.

Каждый запуск должен делать новый backup config.toml,
если config существует и будет изменён.

==================================================
КРИТИЧЕСКИЕ ОШИБКИ ПРЕДЫДУЩИХ ВЕРСИЙ
==================================================

НЕ ПОВТОРЯТЬ:

1.
Authorization Key напрямую как Bearer.

2.
os.environ.Get

вместо:

os.environ.get

3.
.venv\python.exe

вместо:

.venv\Scripts\python.exe

4.
Полную замену certifi cacert.pem одним сертификатом.

5.
mcp-sdk-python вместо mcp[cli].

6.
requests без установленной зависимости.

7.
python-dotenv без необходимости.

8.
print() в stdout MCP stdio сервера.

9.
Запись access_token на диск.

10.
Сравнение expires_at с asyncio loop time.

11.
Хранение Authorization Key прямо в config.toml.

12.
Только process-local $env:
без сохранения User Environment Variable.

13.
Bash syntax:

<<EOF

в PowerShell.

14.
Фальшивый MCP test,
который на самом деле не выполняет tools/list.

15.
README про Cursor/Windsurf вместо Codex.

==================================================
BUILD SCRIPT
==================================================

02_BUILD_PACKAGE.ps1 должен:

- использовать Set-StrictMode;
- использовать $ErrorActionPreference = "Stop";
- создать OutputDir;
- безопасно перезаписать только файлы внутри OutputDir;
- записывать файлы UTF-8;
- использовать PowerShell here-strings там, где удобно;
- НЕ выполнять install.ps1;
- НЕ выполнять install.bat;
- НЕ обращаться в интернет;
- НЕ менять систему.

После создания файлов он должен проверить:

Test-Path install.bat
Test-Path install.ps1
Test-Path server.py
Test-Path README.md

Если всё создано:

вывести:

BUILD PACKAGE SUCCESS

и полный путь OutputDir.

==================================================
САМОПРОВЕРКА ПЕРЕД ФИНАЛЬНЫМ ОТВЕТОМ
==================================================

Перед выдачей PowerShell-кода ты ОБЯЗАН самостоятельно проверить:

- PowerShell quoting;
- PowerShell here-strings;
- вложенные кавычки;
- server.py не изменён архитектурно;
- нет print() в stdout server.py;
- правильный OAuth flow;
- правильный certifi flow;
- правильный venv path;
- правильные pip packages;
- Authorization Key не попадает в файлы/логи/config;
- access_token не выводится;
- config.toml сохраняет чужие секции;
- MCP tools/list является настоящим тестом;
- stdio tools/list является настоящим тестом;
- install.ps1 идемпотентен;
- install.bat использует %~dp0;
- README относится к Codex;
- builder ничего не устанавливает и не запускает.

Если сомневаешься между собственной идеей
и жёстким требованием из этой задачи —

ЖЁСТКОЕ ТРЕБОВАНИЕ ИМЕЕТ ПРИОРИТЕТ.

==================================================
ФИНАЛ
==================================================

Верни ТОЛЬКО содержимое:

02_BUILD_PACKAGE.ps1

То есть чистый PowerShell-код.

Никакого markdown.
Никакого анализа.
Никаких альтернатив.
Никаких вопросов.
Никаких рекомендаций.

Выполни спецификацию буквально.