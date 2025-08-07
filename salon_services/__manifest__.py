{
    'name' : "Salon Service",
    'summary' : """
    Modul untuk mengatur daftar layanan salon
    """,
    'author' : "Tim IT Salon",
    'depends' : ['base'],
    'data' : [
        "views/services.xml",
        "views/sub_category.xml",
        "views/category.xml",
        "views/packages.xml",
        "views/dashboard.xml",
        "views/menu.xml",
        "security/ir.model.access.csv",
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