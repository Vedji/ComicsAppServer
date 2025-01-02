import server


if __name__ == '__main__':
    app = server.create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
