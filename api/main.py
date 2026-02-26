from website import create_app

def start_webserver():
    """Start the Flask development server for the door-opener API."""
    print("Starting web server...")

    create_app().run(debug=True, host="0.0.0.0", port=4000)

if __name__ == "__main__":
    start_webserver()
