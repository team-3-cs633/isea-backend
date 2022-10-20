from api import app, local_environment


if __name__ == "__main__":
    if local_environment:
        app.run(debug=True, port=5555)
    else:
        app.run(host="0.0.0.0", port=5555)
