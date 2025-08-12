{
    'name' : "Salon Hospitality",
    'summary' : """
    Modul untuk mengatur manajemen dan jalan usaha salon
    """,
    'author' : "Tim IT Salon",
    'depends' : ['base', 'hr', 'calendar', 'mail', 'product', 'account'],
    'data' : [
        "views/services.xml",
        "views/sub_category.xml",
        "views/category.xml",
        "views/packages.xml",
        "views/branches.xml",
        "views/branches_manager.xml",
        "views/booking.xml",
        "views/customer.xml",
        "views/calendar.xml",
        "views/staff.xml",
        "views/dashboard.xml",
        "views/menu.xml",
        "security/ir.model.access.csv",
        "data/ir.sequence.xml",
    ],
    "assets" : {
    "web.assets_backend" : [
        "salon_services/static/src/components/**/*.js",
        "salon_services/static/src/components/**/*.xml",
        "salon_services/static/src/scss/**/*.scss",
        "salon_services/static/src/img/**/*.png"
        ]
    },
    'application' : True,
}