
{
    'name': 'Personalizaciones de Mantenimiento',
    'version': '1.0',
    'summary': 'Añade campos de tipo y categoría a equipos de mantenimiento',
    'author': 'jbarreto',
    'category': 'Mantenimiento',
    
    
    'depends': [
        'base',
        'maintenance', 
        'hr_maintenance',
        'project',
        'stock',
        'account',
        'hr'
    ],
    
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/mantenimiento_equipo_view.xml',  
        'views/mantenimiento_solicitud_view.xml',
        'report/mantenimiento_report.xml',
        'views/mantenimiento_programacion_view.xml',
        'report/programacion_report.xml',
        'views/account_analytic_view.xml',
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
}