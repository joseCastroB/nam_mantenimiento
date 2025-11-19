
{
    'name': 'Personalizaciones de Mantenimiento',
    'version': '1.0',
    'summary': 'Añade campos de tipo y categoría a equipos de mantenimiento',
    'author': 'jbarreto',
    'category': 'Mantenimiento',
    
    
    'depends': [
        'maintenance',
    ],
    
    'data': [
        'security/ir.model.access.csv',
        'views/mantenimiento_equipo_view.xml',  
        'views/mantenimiento_solicitud_view.xml'
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
}