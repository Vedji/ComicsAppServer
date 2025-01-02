import server


if __name__ == '__main__':
    app = server.create_app()
    app.run(port=5000, debug=True)