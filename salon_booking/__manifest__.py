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
        "views/dashboard.xml",
        "views/menu.xml",
        "security/ir.model.access.csv",
    ],
    "assets" : {
    "web.assets_backend" : [
        "salon_booking/static/src/components/**/*.js",
        "salon_booking/static/src/components/**/*.xml",
        "salon_booking/static/src/scss/**/*.scss",
        "salon_booking/static/src/img/**/*.png"
        ]
    },
    'application' : True,
}