# C:/Users/hp/odoo-dev/custom-addons/mi_modulo_mantenimiento/__manifest__.py

{
    'name': 'Personalizaciones de Mantenimiento',
    'version': '1.0',
    'summary': 'Añade campos de tipo y categoría a equipos de mantenimiento',
    'author': 'Tu Nombre (jbarreto)',
    'category': 'Mantenimiento',
    
    # ¡La parte más importante!
    # Le dice a Odoo que este módulo NO PUEDE funcionar
    # si el módulo 'maintenance' (Mantenimiento) no está instalado.
    'depends': [
        'maintenance',
    ],
    
    # Aquí es donde le diremos a Odoo que cargue nuestros
    # archivos de Python y XML (los crearemos después)
    'data': [
        'security/ir.model.access.csv',
        'views/mantenimiento_equipo_view.xml',  
        'views/mantenimiento_solicitud_view.xml'
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
}