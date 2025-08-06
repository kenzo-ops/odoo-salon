{
    'name' : "Salon Booking",
    'summary' : """
    Modul untuk mengatur sistem booking salon
    """,
    'author' : "Tim IT Salon",
    'depends' : ['base', 'salon_services','calendar'],
    'data' : [
        "data/ir.sequence.xml",
        "views/booking.xml",
        "views/calendar.xml",
        "views/menu.xml",
        "security/ir.model.access.csv",
    ],
    'application' : True,
}