from ozevent import db, create_app

# Create Database Instance
app = create_app()
ctx = app.app_context()
ctx.push()
db.create_all()
quit()