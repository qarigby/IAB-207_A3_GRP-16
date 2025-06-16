from datetime import date, time
from flask_bcrypt import generate_password_hash
from ozevent import create_app, db
from ozevent.models import Event, User

app = create_app()
app.app_context().push()

# Optional: clear old logs
Event.query.delete()
User.query.delete()

# Add new sample events
events = [
    Event(
        title="Let It Be (UK)",
        genre="Rock",
        venue="Fortitude Valley Music Hall",
        location="Fortitude Valley, Brisbane",
        date=date(2025, 5, 30),
        start_time=time(20, 0),
        end_time=time(22, 0),
        status="Open",
        available_tickets=200,
        ticket_price=200,
        short_description="Experience the unique magic of The Beatles with this incredible tribute act from the UK.",
        description="Join us for a magical evening of timeless classics performed by the UK's best Beatles tribute band.",
        image="beatles_tribute.jpg",
        owner_id=1
    ),
    Event(
        title="Seven Wonders",
        genre="Pop",
        venue="Brisbane Powerhouse",
        location="New Farm, Brisbane",
        date=date(2025, 6, 10),
        start_time=time(18, 0),
        end_time=time(20, 0),
        status="Open",
        available_tickets=150,
        ticket_price=110,
        short_description="Treat yourself to relaxing ocean tones with this rock outfit from the coast of Spain.",
        description="Experience the harmonies and hits of Fleetwood Mac with this spectacular Spanish tribute band.",
        image="acoustic_act.jpg",
        owner_id=1
    ),
    Event(
        title="Orphaned Land",
        genre="Metal",
        venue="Riverstage",
        location="Botanic Gardens, Brisbane",
        date=date(2025, 6, 22),
        start_time=time(21, 0),
        end_time=time(23, 0),
        status="Open",
        available_tickets=500,
        ticket_price=50,
        short_description="Hear the thunderous roar of modern prog metal with this award-winning Israeli band.",
        description="Middle Eastern melodies and metal riffs collide in this unique live performance from Orphaned Land.",
        image="metal_band.jpg",
        owner_id=1
    ),
    Event(
        title="Eminem Live",
        genre="Hip Hop",
        venue="Suncorp Stadium",
        location="Milton, Brisbane",
        date=date(2025, 8, 1),
        start_time=time(20, 0),
        end_time=time(22, 30),
        status="Cancelled",
        available_tickets=1000,
        ticket_price=250,
        short_description="Feel the raw energy and wordful mastery of Eminem, Detroit's very own lyrical miracle.",
        description="Eminem was scheduled to deliver a high-energy set with iconic tracks. This event has since been cancelled.",
        image="eminem_concert.jpg",
        owner_id=1
    ),
    Event(
        title="Atlanta Symphony",
        genre="Classical",
        venue="Entertainment Centre",
        location="Boondall, Brisbane",
        date=date(2025, 7, 14),
        start_time=time(19, 30),
        end_time=time(21, 30),
        status="Sold Out",
        available_tickets=300,
        ticket_price=75,
        short_description="Experience the timeless brilliance of classical music with the Atlanta Symphony Orchestra.",
        description="An enchanting evening of symphonic masterpieces performed by the world-renowned Atlanta Symphony Orchestra.",
        image="live_orchestra.jpg",
        owner_id=1
    ),
    Event(
        title="Kurt Baker",
        genre="Rock",
        venue="Brisbane Convention Centre",
        location="South Bank, Brisbane",
        date=date(2025, 1, 25),
        start_time=time(18, 30),
        end_time=time(20, 00),
        status="Inactive",
        available_tickets=150,
        ticket_price=80,
        short_description="Catch the electrifying energy of Kurt Baker as he rocks the stage with infectious tunes.",
        description="Experience the high-voltage thrill of Kurt Baker live in concert, where every performance crackles with raw energy and unstoppable rhythm. Known for his infectious blend of power pop, punk, and rock 'n' roll, Kurt lights up the stage with catchy hooks, driving beats, and a magnetic presence that pulls the crowd into the heart of the show. Whether you're a longtime fan or a newcomer to his sound, get ready to dance, sing, and lose yourself in a night of pure, electrifying fun.",
        image="kurt_baker.jpg",
        owner_id=1
    ),
]

# Add new sample users
users = [
    User(
        firstname="John",
        surname="Jackson",
        username="john.jackson",
        email="johnnyjacko84@gmail.com",
        profile_pic="john_jackson.jpg",
        phone_number="0435789452",
        street_address="123 Smithers Street",
        password_hash=generate_password_hash("john123!"),
        ),
    User(
        firstname="Amanda",
        surname="Smith",
        username="amanda.smith",
        email="asmith@hotmail.com",
        profile_pic="amanda_smith.jpg",
        phone_number="0412345678",
        street_address="456 Elm Street",
        password_hash=generate_password_hash("amanda123!"),
    ),
    User(
        firstname="Leroy",
        surname="Jenkins",
        username="leroy.jenkins",
        email="leejenkster@gmail.com",
        profile_pic="leroy_jenkins.jpg",
        phone_number="0423456789",
        street_address="789 Oak Street",
        password_hash=generate_password_hash("leroy123!"),
    ),
]

db.session.add_all(events)
db.session.add_all(users)
db.session.commit()

print("Seeded 6 new demo events and 3 new users into the database")