from api_v1 import create_app

# Создаем приложение
app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
