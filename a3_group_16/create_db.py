from ozevent import db, create_app

# File for creating the database instance

app = create_app()
ctx = app.app_context()
ctx.push()
db.create_all()
quit()