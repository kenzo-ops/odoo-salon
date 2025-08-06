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
        "views/menu.xml",
        "security/ir.model.access.csv",
    ],
    'application' : True,
}