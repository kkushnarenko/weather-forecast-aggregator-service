import uvicorn

if __name__ == "__main__":
    # Запускаем приложение app из модуля src.main
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Автоматическая перезагрузка при изменении кода
    )