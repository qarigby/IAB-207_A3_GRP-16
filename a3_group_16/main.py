from ozevent import create_app

# Initialise/Run Web App
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) # Set to false in deployment