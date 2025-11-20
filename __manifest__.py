
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
        'data/mantenimiento_sequence.xml',
        'views/mantenimiento_equipo_view.xml',  
        'views/mantenimiento_solicitud_view.xml',
        'report/mantenimiento_report.xml',
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
}