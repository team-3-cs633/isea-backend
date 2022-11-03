from api import app


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5555,
        ssl_context=("./.certs/cert.pem", "./.certs/key.pem")
    )
