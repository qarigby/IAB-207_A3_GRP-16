from datetime import date, time
from flask_bcrypt import generate_password_hash
from ozevent import create_app, db
from ozevent.models import Booking, Event, Ticket, User

app = create_app()
app.app_context().push()

# Optional: clear old logs
db.session.query(Event).delete()
db.session.query(Ticket).delete()
db.session.query(Booking).delete()
db.session.query(User).delete()
db.session.commit()

# Add new sample events
events = [
    Event(
        title="Let It Be",
        genre="Rock",
        venue="Fortitude Valley Music Hall",
        location="Fortitude Valley, Brisbane",
        date=date(2025, 7, 30),
        start_time=time(20, 0),
        end_time=time(22, 0),
        status="Open",
        short_description="Experience the unique magic of The Beatles with this incredible tribute act from the UK.",
        description="Step into a world of nostalgia and musical brilliance as Let It Be (UK) brings the unforgettable sound of The Beatles to life. This acclaimed tribute act from the UK delivers a captivating performance, recreating the iconic harmonies, energy, and charisma that made The Beatles legendary. Sing along to timeless classics, relive the golden era of rock, and immerse yourself in a night filled with the spirit and magic of the Fab Four. Perfect for fans of all ages, this show promises an authentic and exhilarating Beatles experience.",
        image="/static/img/beatles_tribute.jpg",
        owner_id=1
    ),
    Event(
        title="Seven Wonders",
        genre="Pop",
        venue="Brisbane Powerhouse",
        location="New Farm, Brisbane",
        date=date(2025, 8, 10),
        start_time=time(18, 0),
        end_time=time(20, 0),
        status="Open",
        short_description="Treat yourself to relaxing ocean tones with this rock outfit from the coast of Spain.",
        description="Let the soothing sounds of Seven Wonders transport you to the sun-kissed shores of Spain. This talented rock group blends oceanic melodies with pop sensibilities, creating a relaxing yet invigorating musical journey. Enjoy a night of smooth vocals, intricate guitar work, and captivating rhythms that evoke the beauty and tranquility of the coast. Whether you're a fan of pop, rock, or simply great live music, Seven Wonders promises an unforgettable evening of musical escape.",
        image="/static/img/acoustic_act.jpg",
        owner_id=1
    ),
    Event(
        title="Orphaned Land",
        genre="Metal",
        venue="Riverstage",
        location="Botanic Gardens, Brisbane",
        date=date(2025, 8, 22),
        start_time=time(21, 0),
        end_time=time(23, 0),
        status="Open",
        short_description="Hear the thunderous roar of modern prog metal with this award-winning Israeli band.",
        description="Prepare for a powerful night as Orphaned Land, Israel's award-winning progressive metal band, takes the stage. Fusing thunderous metal riffs with Middle Eastern melodies, their music is a unique blend of cultures and sounds. Experience the intensity, passion, and technical mastery that have earned them a global following. This is more than just a concert—it's a musical journey that breaks boundaries and unites fans through the universal language of metal.",
        image="/static/img/metal_band.jpg",
        owner_id=1
    ),
    Event(
        title="Eminem",
        genre="Hip Hop",
        venue="Suncorp Stadium",
        location="Milton, Brisbane",
        date=date(2025, 9, 1),
        start_time=time(20, 0),
        end_time=time(22, 30),
        status="Cancelled",
        short_description="Feel the raw energy and wordful mastery of Eminem, Detroit's very own lyrical miracle.",
        description="Eminem, Detroit's legendary wordsmith, was set to electrify Suncorp Stadium with his signature blend of raw energy, rapid-fire lyrics, and unforgettable stage presence. Fans anticipated a night packed with chart-topping hits, emotional storytelling, and the kind of intensity only Eminem can deliver. Although this event has been cancelled, the excitement and anticipation surrounding his performance remain a testament to his enduring impact on hip hop and music lovers worldwide.",
        image="/static/img/eminem_concert.jpg",
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
        short_description="Experience the timeless brilliance of classical music with the Atlanta Symphony Orchestra.",
        description="Join the world-renowned Atlanta Symphony Orchestra for an enchanting evening of classical masterpieces. Let the orchestra's exquisite musicianship and passion for music sweep you away as they perform works by the greatest composers in history. From stirring symphonies to delicate chamber pieces, this sold-out concert promises a night of elegance, emotion, and unforgettable artistry. Perfect for classical aficionados and newcomers alike, this is a musical event not to be missed.",
        image="/static/img/live_orchestra.jpg",
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
        short_description="Catch the electrifying energy of Kurt Baker as he rocks the stage with infectious tunes.",
        description="Get ready for a high-voltage night as Kurt Baker brings his infectious energy and catchy rock tunes to the stage. Known for his dynamic performances and blend of power pop, punk, and classic rock, Kurt delivers a show packed with driving beats, sing-along choruses, and a magnetic stage presence. Whether you're a longtime fan or new to his music, this concert promises a fun-filled, electrifying experience that will have you dancing and singing all night long.",
        image="/static/img/kurt_baker.jpg",
        owner_id=1
    ),
    Event(
        title="Rocktober Festival",
        genre="Rock",
        venue="Brisbane Showgrounds",
        location="Bowen Hills, Brisbane",
        date=date(2025, 10, 25),
        start_time=time(18, 00),
        end_time=time(23, 00),
        status="Open",
        short_description="Brisbane's biggest rock festival with live bands, food and fun for everyone.",
        description="Rocktober Festival is Brisbane's ultimate celebration of rock music, bringing together legendary acts, rising stars and passionate fans for an unforgettable day and night of live performances. Set across multiple stages at the iconic Brisbane Showgrounds, the festival features a diverse lineup spanning classic rock, indie, punk and alternative genres. Enjoy electrifying sets from headline bands, discover new favourites and immerse yourself in the vibrant festival atmosphere with gourmet food trucks, craft beer gardens and interactive art installations. Whether you're a die-hard rocker or just looking for a great time with friends, Rocktober Festival promises high-energy music, community spirit and memories that will last a lifetime. Don't miss out on Brisbane's biggest rock event of the year!",
        image=None,
        owner_id=1
    )
]

# Add new sample users
users = [
    User(
        firstname="John",
        surname="Jackson",
        username="john.jackson",
        email="johnnyjacko84@gmail.com",
        profile_pic="/static/img/john_jackson.jpg",
        phone_number="0435789452",
        street_address="123 Smithers Street",
        password_hash=generate_password_hash("john123!"),
        ),
    User(
        firstname="Amanda",
        surname="Smith",
        username="amanda.smith",
        email="asmith@hotmail.com",
        profile_pic="/static/img/amanda_smith.jpg",
        phone_number="0412345678",
        street_address="456 Elm Street",
        password_hash=generate_password_hash("amanda123!"),
    ),
    User(
        firstname="Leroy",
        surname="Jenkins",
        username="leroy.jenkins",
        email="leejenkster@bigpond.com",
        profile_pic="/static/img/leroy_jenkins.jpg",
        phone_number="0423456789",
        street_address="789 Oak Street",
        password_hash=generate_password_hash("leroy123!"),
    ),
    User(
        firstname="Quinn",
        surname="Rigby",
        username="quinn.rigby",
        email="quinn.rigby@outlook.com",
        profile_pic=None, # Despises profile pictures, should = default
        phone_number="0456789123",
        street_address="321 Pine Street",
        password_hash=generate_password_hash("quinn123!"),
    )
]

tickets = [
    Ticket(
        ticket_type = "GA",
        available_tickets = 150,
        ticket_price = 89.99,
        event_id = 1
    ),
    Ticket(
        ticket_type = "VIP",
        available_tickets = 50,
        ticket_price = 180.00,
        event_id = 1
    ),
    Ticket(
        ticket_type = "GA",
        available_tickets = 150,
        ticket_price = 109.99,
        event_id = 2
    ),
    Ticket(
        ticket_type = "GA",
        available_tickets = 300,
        ticket_price = 69.99,
        event_id = 3
    ),
    Ticket(
        ticket_type = "VIP",
        available_tickets = 150,
        ticket_price = 140.00,
        event_id = 3
    ),
    Ticket(
        ticket_type = "VIP+",
        available_tickets = 50,
        ticket_price = 200.00,
        event_id = 3
    ),
    Ticket(
        ticket_type = "GA",
        available_tickets = 0,
        ticket_price = 179.99,
        event_id = 4
    ),
    Ticket(
        ticket_type = "GA",
        available_tickets = 0,
        ticket_price = 99.99,
        event_id = 5
    ),
    Ticket(
        ticket_type = "GA",
        available_tickets = 100,
        ticket_price = 84.99,
        event_id = 6
    ),
    Ticket(
        ticket_type = "VIP",
        available_tickets = 50,
        ticket_price = 120.00,
        event_id = 6
    ),
    Ticket(
        ticket_type = "GA",
        available_tickets = 200,
        ticket_price = 54.99,
        event_id = 7
    )
]

db.session.add_all(events)
db.session.add_all(tickets)
db.session.add_all(users)
db.session.commit()

print("Seeded 6 new events and 4 new users into the database")