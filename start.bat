REM Проверка наличия директорий
if not exist "data" (
    echo Создание директории data...
    mkdir data
)

if not exist "logs" (
    echo Создание директории logs...
    mkdir logs
)

docker compose up -d