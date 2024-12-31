from api_v1 import create_app

# Создаем приложение
app = create_app()


if __name__ == '__main__':
    app.run(port=5000, debug=True)
