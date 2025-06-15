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
        ticket_price=200,
        short_description="Experience the unique magic of The Beatles with this incredible tribute act from the UK.",
        description="Join us for a magical evening of timeless classics performed by the UK's best Beatles tribute band.",
        image="beatles_tribute.jpg",
        owner_id=1
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
        ticket_price=175,
        short_description="Treat yourself to relaxing ocean tones with this rock outfit from the coast of Spain.",
        description="Experience the harmonies and hits of Fleetwood Mac with this spectacular Spanish tribute band.",
        image="acoustic_act.jpg",
        owner_id=1
    ),
    Event(
        name="Orphaned Land",
        genre="metal",
        venue="Riverstage",
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
        name="Eminem Live",
        genre="hip hop",
        venue="Suncorp Stadium",
        date=date(2025, 8, 1),
        start_time=time(20, 0),
        end_time=time(22, 30),
        status="Cancelled",
        available_tickets=1000,
        ticket_price=300,
        short_description="Feel the raw energy and wordful mastery of Eminem, Detroit's very own lyrical miracle.",
        description="Eminem was scheduled to deliver a high-energy set with iconic tracks. This event has since been cancelled.",
        image="eminem_concert.jpg",
        owner_id=1
    ),
    Event(
        name="Atlanta Symphony",
        genre="classical",
        venue="Entertainment Centre",
        date=date(2025, 7, 14),
        start_time=time(19, 30),
        end_time=time(21, 30),
        status="Sold Out",
        available_tickets=300,
        ticket_price=75,
        short_description="Experience the timeless brilliance of classical music with the Atlanta Symphony Orchestra",
        description="An enchanting evening of symphonic masterpieces performed by the world-renowned Atlanta Symphony Orchestra.",
        image="live_orchestra.jpg",
        owner_id=1
    ),
    Event(
        name="Kurt Baker",
        genre="rock",
        venue="Brisbane Convention Centre",
        date=date(2025, 1, 25),
        start_time=time(18, 30),
        end_time=time(20, 00),
        status="Inactive",
        available_tickets=150,
        ticket_price=150,
        short_description="Catch the electrifying energy of Kurt Baker as he rocks the stage with infectious tunes.",
        description="Experience the high-voltage thrill of Kurt Baker live in concert, where every performance crackles with raw energy and unstoppable rhythm. Known for his infectious blend of power pop, punk, and rock 'n' roll, Kurt lights up the stage with catchy hooks, driving beats, and a magnetic presence that pulls the crowd into the heart of the show. Whether you're a longtime fan or a newcomer to his sound, get ready to dance, sing, and lose yourself in a night of pure, electrifying fun.",
        image="kurt_baker.jpg",
        owner_id=1
    ),
]

db.session.add_all(events)
db.session.commit()
print("Seeded 5 demo events into the database.")
