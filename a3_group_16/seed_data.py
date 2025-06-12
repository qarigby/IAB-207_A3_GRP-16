from datetime import date, time
from ozevent import create_app, db
from ozevent.models import Event

app = create_app()
app.app_context().push()

# Optional: clear old events
Event.query.delete()

# Add new sample events
events = [
    Event(
        name="Let It Be (UK)",
        genre="rock",
        venue="Fortitude Valley Music Hall",
        date=date(2025, 5, 30),
        start_time=time(20, 0),
        end_time=time(22, 0),
        status="Open",
        available_tickets=200,
        short_description="A Beatles tribute show from the UK.",
        description="Join us for a magical evening of timeless classics performed by the UK's best Beatles tribute band.",
        image="beatles_tribute.jpg",
        user_id=1
    ),
    Event(
        name="Seven Wonders",
        genre="pop",
        venue="Brisbane Powerhouse",
        date=date(2025, 6, 10),
        start_time=time(18, 0),
        end_time=time(20, 0),
        status="Open",
        available_tickets=150,
        short_description="Fleetwood Mac tribute from Spain.",
        description="Experience the harmonies and hits of Fleetwood Mac with this spectacular Spanish tribute band.",
        image="acoustic_act.jpg",
        user_id=1
    ),
    Event(
        name="Orphaned Land",
        genre="metal",
        venue="Riverstage",
        date=date(2025, 6, 22),
        start_time=time(21, 0),
        end_time=time(23, 0),
        status="Sold Out",
        available_tickets=0,
        short_description="Israeli prog metal band performance.",
        description="Middle Eastern melodies and metal riffs collide in this unique live performance from Orphaned Land.",
        image="metal_band.jpg",
        user_id=1
    ),
    Event(
        name="Eminem Live",
        genre="hip hop",
        venue="Suncorp Stadium",
        date=date(2025, 8, 1),
        start_time=time(20, 0),
        end_time=time(22, 30),
        status="Cancelled",
        available_tickets=0,
        short_description="The Rap God returns to Brisbane.",
        description="Eminem was scheduled to deliver a high-energy set with iconic tracks. This event has since been cancelled.",
        image="eminem_concert.jpg",
        user_id=1
    ),
    Event(
        name="Atlanta Symphony",
        genre="classical",
        venue="Entertainment Centre",
        date=date(2025, 7, 14),
        start_time=time(19, 30),
        end_time=time(21, 30),
        status="Inactive",
        available_tickets=0,
        short_description="A night of classical symphony music.",
        description="An enchanting evening of symphonic masterpieces performed by the world-renowned Atlanta Symphony Orchestra.",
        image="live_orchestra.jpg",
        user_id=1
    ),
]

db.session.add_all(events)
db.session.commit()
print("✅ Seeded 5 demo events into the database.")
