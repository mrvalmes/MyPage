from extensions import db
from models import VentasDetalle, Objetivos, Pagos
from sqlalchemy import func, cast, extract, or_, text, case, and_
from datetime import datetime, timedelta

def get_chart_data(anio="2025", empleado_id=None, supervisor_id=None):
    query = db.session.query(
        VentasDetalle.tipo_venta,
        cast(extract('month', VentasDetalle.fecha), db.Integer).label('mes'),
        func.sum(VentasDetalle.total_ventas).label('total')
    ).filter(
        cast(extract('year', VentasDetalle.fecha), db.String) == anio,
        VentasDetalle.entity_code != 'EX332'
    )

    if empleado_id:
        query = query.filter(VentasDetalle.usuario_creo_orden.like(empleado_id + " - %"))

    if supervisor_id:
        query = query.filter(VentasDetalle.supervisor == supervisor_id)

    query = query.group_by(VentasDetalle.tipo_venta, 'mes') \
                 .order_by(VentasDetalle.tipo_venta, 'mes')
    
    rows = query.all()

    data_dict = {}
    for tipo_venta, mes, total in rows:
        if tipo_venta not in data_dict:
            data_dict[tipo_venta] = [0] * 12
        data_dict[tipo_venta][mes - 1] = total

    groups_map = {
        "Card": ["Card"],
        "Flex/Max": ["Flex/Max"],
        "Internet": ["Internet"],
        "Migraciones": ["Migraciones", "Migraciones Net"],
        "Fidepuntos Pos": ["Fidepuntos Pospago", "Fidepuntos Disminucion"],
        "Fidepuntos Up": ["Fidepuntos Aumento"],
        "Reemplazo Pos": ["Reemplazo Pospago", "Reemplazo Disminucion"],
        "Reemplazo Up": ["Reemplazo Aumento"],
        "Fide Reemp Internet Up": [
            "Reemplazo Internet",
            "Fidepuntos Internet",
            "Fidepuntos InternetAum",
            "Fidepuntos InternetDism",
            "Reemplazo InternetAum",
            "Reemplazo InternetDism",
        ],
        "Aumentos": ["Aumentos Pospago", "Aumentos Internet"],
    }

    agrupado_dict = {}
    for categoria in groups_map:
        agrupado_dict[categoria] = [0] * 12

    for categoria, lista_tipos in groups_map.items():
        for tv in lista_tipos:
            if tv in data_dict:
                for i in range(12):
                    agrupado_dict[categoria][i] += data_dict[tv][i]

    labels = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ]

    color_map = {
        "Card": "rgba(255, 255, 0, 1)",
        "Flex/Max": "rgba(1, 126, 250, 1)",
        "Internet": "rgba(0, 255, 0, 1)",
        "Migraciones": "rgba(155, 89, 182, 1)",
        "Fidepuntos Pos": "rgba(46, 204, 113, 1)",
        "Fidepuntos Up": "rgba(243, 156, 18, 1)",
        "Reemplazo Pos": "rgba(52, 152, 219, 1)",
        "Reemplazo Up": "rgba(26, 188, 156, 1)",
        "Fide Reemp Internet Up": "rgba(231, 76, 60, 1)",
        "Aumentos": "rgba(128, 128, 128, 0.5)",
    }

    datasets = []
    for cat, values in agrupado_dict.items():
        datasets.append(
            {
                "label": cat,
                "data": values,
                "backgroundColor": color_map.get(cat, "rgba(0,0,0,0.5)"),
                "borderColor": color_map.get(cat, "rgba(0,0,0,1)"),
                "borderWidth": 2,
            }
        )

    return {"labels": labels, "datasets": datasets}

def get_chart_data_logro(anio="2025", empleado_id=None, supervisor_id=None):
    select_cols = [
        VentasDetalle.tipo_venta,
        cast(extract('month', VentasDetalle.fecha), db.Integer).label('mes'),
        func.sum(VentasDetalle.total_ventas).label('total_ventas'),
        Objetivos.sim_card_prepago,
        Objetivos.flex_max,
        Objetivos.internet_pospago,
        Objetivos.migraciones_pospago_net,
        Objetivos.fidepuntos_pospago,
        Objetivos.fidepuntos_up,
        Objetivos.reemplazo_pospago,
        Objetivos.reemplazo_up,
        Objetivos.fide_reemp_internet_up,
        Objetivos.aumentos_plan_pos_net
    ]

    base_query = db.session.query(*select_cols).filter(
        cast(extract('year', VentasDetalle.fecha), db.String) == anio
    )
    
    if empleado_id and empleado_id.lower() != "none":
        base_query = base_query.outerjoin(
            Objetivos,
            (VentasDetalle.usuario_creo_orden.like(Objetivos.id_empleado + ' - %')) &
            (cast(extract('year', Objetivos.fecha), db.String) == anio) &
            (extract('month', Objetivos.fecha) == extract('month', VentasDetalle.fecha))
        ).filter(
            VentasDetalle.usuario_creo_orden.like(empleado_id + ' - %')
        )
    elif supervisor_id and supervisor_id.lower() != "none":
        base_query = base_query.outerjoin(
            Objetivos,
            (VentasDetalle.supervisor == Objetivos.id_empleado) & 
            (cast(extract('year', Objetivos.fecha), db.String) == anio) &
            (extract('month', Objetivos.fecha) == extract('month', VentasDetalle.fecha))
        ).filter(
            VentasDetalle.supervisor == supervisor_id
        )
    else:
        base_query = base_query.outerjoin(
            Objetivos,
            (cast(extract('year', Objetivos.fecha), db.String) == anio) &
            (extract('month', Objetivos.fecha) == extract('month', VentasDetalle.fecha))
        )

    base_query = base_query.group_by(
        VentasDetalle.tipo_venta, 'mes',
        Objetivos.sim_card_prepago, Objetivos.flex_max, Objetivos.internet_pospago,
        Objetivos.migraciones_pospago_net, Objetivos.fidepuntos_pospago,
        Objetivos.fidepuntos_up, Objetivos.reemplazo_pospago, Objetivos.reemplazo_up,
        Objetivos.fide_reemp_internet_up, Objetivos.aumentos_plan_pos_net
    ).order_by(
        VentasDetalle.tipo_venta, 'mes'
    )

    rows = base_query.all()
    
    raw_ventas = {}
    raw_obj = {}

    for (
        tipo_venta, mes, total_ventas, sim_card_prepago, flex_max, internet_pospago,
        migraciones_pospago_net, fidepuntos_pospago, fidepuntos_up, reemplazo_pospago,
        reemplazo_up, fide_reemp_internet_up, aumentos_plan_pos_net,
    ) in rows:
        if tipo_venta not in raw_ventas:
            raw_ventas[tipo_venta] = [0] * 12
            raw_obj[tipo_venta] = [0] * 12

        raw_ventas[tipo_venta][mes - 1] += total_ventas

        objetivo_val = 0
        if tipo_venta == "Card": objetivo_val = sim_card_prepago or 0
        elif tipo_venta == "Flex/Max": objetivo_val = flex_max or 0
        elif tipo_venta == "Internet": objetivo_val = internet_pospago or 0
        elif tipo_venta == "Migraciones": objetivo_val = migraciones_pospago_net or 0
        elif tipo_venta in ("Fidepuntos Pospago", "Fidepuntos Disminucion"): objetivo_val = fidepuntos_pospago or 0
        elif tipo_venta == "Fidepuntos Aumento": objetivo_val = fidepuntos_up or 0
        elif tipo_venta in ("Reemplazo Pospago", "Reemplazo Disminucion"): objetivo_val = reemplazo_pospago or 0
        elif tipo_venta == "Reemplazo Aumento": objetivo_val = reemplazo_up or 0
        elif tipo_venta == "Fide Reemp Internet Up": objetivo_val = fide_reemp_internet_up or 0
        elif tipo_venta in ("Aumentos Pospago", "Aumentos Internet"): objetivo_val = aumentos_plan_pos_net or 0

        raw_obj[tipo_venta][mes - 1] += objetivo_val

    groups_map = {
        "Card": ["Card"],
        "Flex/Max": ["Flex/Max"],
        "Internet": ["Internet"],
        "Migraciones": ["Migraciones", "Migraciones Net"],
        "Fidepuntos Pos": ["Fidepuntos Pospago", "Fidepuntos Disminucion"],
        "Fidepuntos Up": ["Fidepuntos Aumento"],
        "Reemplazo Pos": ["Reemplazo Pospago", "Reemplazo Disminucion"],
        "Reemplazo Up": ["Reemplazo Aumento"],
        "Fide Reemp Internet Up": [
            "Reemplazo Internet", "Fidepuntos Internet", "Fidepuntos InternetAum",
            "Fidepuntos InternetDism", "Reemplazo InternetAum", "Reemplazo InternetDism",
        ],
        "Aumentos": ["Aumentos Pospago", "Aumentos Internet"],
    }

    final_ventas = {}
    final_obj = {}
    for cat in groups_map.keys():
        final_ventas[cat] = [0] * 12
        final_obj[cat] = [0] * 12

    for cat, lista_tipos in groups_map.items():
        for tv in lista_tipos:
            if tv in raw_ventas:
                for i in range(12):
                    final_ventas[cat][i] += raw_ventas[tv][i]
                    final_obj[cat][i] += raw_obj[tv][i]

    logro_dict = {}
    for cat in groups_map.keys():
        logro_dict[cat] = [0] * 12
        for i in range(12):
            obj_val = final_obj[cat][i]
            ven_val = final_ventas[cat][i]
            if obj_val > 0:
                logro_dict[cat][i] = round((ven_val / obj_val) * 100, 2)
            else:
                logro_dict[cat][i] = 0

    labels = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ]

    color_map = {
        "Card": "rgba(255, 255, 0, 1)",
        "Flex/Max": "rgba(1, 126, 250, 1)",
        "Internet": "rgba(0, 255, 0, 1)",
        "Migraciones": "rgba(155, 89, 182, 1)",
        "Fidepuntos Pos": "rgba(46, 204, 113, 1)",
        "Fidepuntos Up": "rgba(243, 156, 18, 1)",
        "Reemplazo Pos": "rgba(52, 152, 219, 1)",
        "Reemplazo Up": "rgba(26, 188, 156, 1)",
        "Fide Reemp Internet Up": "rgba(231, 76, 60, 1)",
        "Aumentos": "rgba(128, 128, 128, 0.5)",
    }

    datasets = []
    for cat in groups_map.keys():
        datasets.append(
            {
                "label": cat,
                "data": logro_dict[cat],
                "backgroundColor": color_map.get(cat, "rgba(0,0,0,0.5)"),
                "borderColor": color_map.get(cat, "rgba(0,0,0,1)"),
                "borderWidth": 2,
            }
        )

    return {"labels": labels, "datasets": datasets}

def get_rank_pav_cc():
    """
    Retorna los top 10 usuarios (usuario_creo_orden) y su suma de ventas
    para el mes/año actual, excluyendo entity_code '44066'.
    """
    now = datetime.now()
    
    query = db.session.query(
        VentasDetalle.usuario_creo_orden,
        func.sum(VentasDetalle.total_ventas).label('total_ventas')
    ).filter(
        VentasDetalle.tipo_venta != 'Card',
        VentasDetalle.entity_code != '44066',
        extract('year', VentasDetalle.fecha) == now.year,
        extract('month', VentasDetalle.fecha) == now.month
    ).group_by(VentasDetalle.usuario_creo_orden) \
     .order_by(func.sum(VentasDetalle.total_ventas).desc()) \
     .limit(10)
    
    return query.all()

def get_top_sales(start_date=None, end_date=None, limit=10):
    query = db.session.query(
        VentasDetalle.usuario_creo_orden,
        func.sum(VentasDetalle.total_ventas).label('total_pav')
    ).filter(
        VentasDetalle.tipo_venta != 'Card',
        VentasDetalle.tipo_venta != 'CardEquipo',
        VentasDetalle.tipo_venta != 'InternetCard',
        VentasDetalle.entity_code != 'EX332'
    )

    if start_date and end_date:
        query = query.filter(VentasDetalle.fecha.between(start_date, end_date))
    elif start_date:
        query = query.filter(VentasDetalle.fecha == start_date)
    elif end_date:
        query = query.filter(VentasDetalle.fecha == end_date)
    else:
        # Filtro por mes actual si no hay fechas
        now = datetime.now()
        query = query.filter(
            extract('year', VentasDetalle.fecha) == now.year,
            extract('month', VentasDetalle.fecha) == now.month
        )
    
    query = query.group_by(VentasDetalle.usuario_creo_orden) \
                 .order_by(func.sum(VentasDetalle.total_ventas).desc()) \
                 .limit(limit)
    
    return query.all()

def get_total_pav(empleado_id=None):
    now = datetime.now()
    query = db.session.query(func.sum(VentasDetalle.total_ventas)).filter(
        VentasDetalle.tipo_venta != 'Card',
        VentasDetalle.entity_code != 'EX332',
        extract('year', VentasDetalle.fecha) == now.year,
        extract('month', VentasDetalle.fecha) == now.month
    )

    if empleado_id and empleado_id.lower() != 'none' and empleado_id.strip() != '':
        query = query.filter(func.substr(VentasDetalle.usuario_creo_orden, 1, 7) == empleado_id)

    result = query.scalar()
    return result if result else 0

def get_recent_activity():
    now = datetime.now()
    # Si es domingo (6 en python weekday donde lunes es 0, pero sqlite strftime %w domingo es 0)
    # En python weekday(): Mon=0, Sun=6. 
    # En SQL strftime('%w'): Sun=0, Sat=6.
    # La logica original usaba strftime('%w', 'now') = '0' -> Domingo.
    # Python datetime.now().strftime('%w') -> Sun=0.
    
    target_date = now
    if target_date.strftime('%w') == '0': # Domingo
        target_date = now - timedelta(days=1) # Usar sabado
    
    query = db.session.query(
        VentasDetalle.usuario_creo_orden,
        VentasDetalle.tipo_venta,
        func.sum(VentasDetalle.total_ventas).label('cantidad')
    ).filter(
        func.date(VentasDetalle.fecha) == target_date.date(),
        VentasDetalle.tipo_venta != 'Card',
        VentasDetalle.entity_code != 'EX332'
    ).group_by(
        VentasDetalle.usuario_creo_orden,
        VentasDetalle.tipo_venta
    ).order_by(text('cantidad DESC')).limit(7)

    return query.all()

def get_sales_overview():
    now = datetime.now()
    
    # Total ventas (sin Card, sin EX332, mes actual)
    total_sales = db.session.query(func.sum(VentasDetalle.total_ventas)).filter(
        VentasDetalle.tipo_venta != 'Card',
        VentasDetalle.entity_code != 'EX332',
        extract('year', VentasDetalle.fecha) == now.year,
        extract('month', VentasDetalle.fecha) == now.month
    ).scalar()

    if not total_sales:
        return {"labels": [], "data": []}

    # Top 5 tipos de venta
    top5_query = db.session.query(
        VentasDetalle.tipo_venta,
        func.sum(VentasDetalle.total_ventas).label('total')
    ).filter(
        VentasDetalle.tipo_venta.in_([
            'Flex/Max', 'Migraciones', 'Internet', 
            'Reemplazo Aumento', 'Aumentos Pospago', 'Aumentos Internet'
        ]),
        VentasDetalle.entity_code != 'EX332',
        extract('year', VentasDetalle.fecha) == now.year,
        extract('month', VentasDetalle.fecha) == now.month
    ).group_by(
        VentasDetalle.tipo_venta
    ).order_by(text('total DESC'))

    top5_sales = top5_query.all()

    labels = []
    data = []
    for tipo_venta, total in top5_sales:
        labels.append(tipo_venta)
        percentage = (total / total_sales) * 100
        data.append(round(percentage, 2))

    return {"labels": labels, "data": data}

def get_conversion_rate(empleado_id, dia):
    try:
        day_date = datetime.strptime(dia, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")

    ventas_por_usuario_cte = db.session.query(
        VentasDetalle.usuario_creo_orden,
        func.substr(VentasDetalle.usuario_creo_orden, 1, 7).label('user_prefix'),
        func.sum(VentasDetalle.total_ventas).label('ventas_count')  # Cambiado de COUNT a SUM
    ).filter(
        VentasDetalle.tipo_venta != 'Card',
        VentasDetalle.entity_code != 'EX332',
        cast(VentasDetalle.fecha, db.Date) == day_date,
        VentasDetalle.supervisor == empleado_id
    ).group_by(VentasDetalle.usuario_creo_orden).cte('ventas_por_usuario')

    pagos_por_prefijo_cte = db.session.query(
        func.substr(Pagos.userlogin, 1, 7).label('user_prefix'),
        func.count(Pagos.id).label('pagos_count')
    ).filter(
        cast(Pagos.dte, db.Date) == day_date
    ).group_by(func.substr(Pagos.userlogin, 1, 7)).cte('pagos_por_prefijo')

    final_query = db.session.query(
        ventas_por_usuario_cte.c.usuario_creo_orden,
        ventas_por_usuario_cte.c.user_prefix,
        ventas_por_usuario_cte.c.ventas_count,
        func.coalesce(pagos_por_prefijo_cte.c.pagos_count, 0).label('pagos_count'),
        func.round(
            cast(
                case(
                    (pagos_por_prefijo_cte.c.pagos_count > 0, 
                     (cast(ventas_por_usuario_cte.c.ventas_count, db.Float) / pagos_por_prefijo_cte.c.pagos_count) * 100),
                    else_=0
                ), db.Numeric  # Cast to NUMERIC before rounding
            ), 2
        ).label('conversion_rate_pct')
    ).outerjoin(
        pagos_por_prefijo_cte,
        ventas_por_usuario_cte.c.user_prefix == pagos_por_prefijo_cte.c.user_prefix
    ).order_by(text('conversion_rate_pct DESC'))

    rows = final_query.all()
    columns = ["usuario_creo_orden", "user_prefix", "ventas_count", "pagos_count", "conversion_rate_pct"]
    return [dict(zip(columns, r)) for r in rows]

def get_total_pagos(empleado_id=None):
    now = datetime.now()
    query = db.session.query(func.count(Pagos.id)).filter(
        extract('year', cast(Pagos.dte, db.Date)) == now.year,
        extract('month', cast(Pagos.dte, db.Date)) == now.month
    )

    if empleado_id and empleado_id.lower() != 'none' and empleado_id.strip() != '':
        query = query.filter(func.substr(Pagos.userlogin, 1, 7) == empleado_id)

    return query.scalar() or 0

def get_total_recargas(empleado_id=None):
    now = datetime.now()
    # Legacy uses: concepto_pago = '876-PAGO/VENTA RECARGA-TRIVISION MONTO VARIA'
    # But user said to use 'Recarga' or 'concepto_pago' field.
    # I will use the legacy string if possible, or a LIKE query.
    # The user previously said: "replace tipo_pago with concepto_pago".
    # And "api_recargas endpoint in blueprints/api.py was updated to filter by concepto_pago="Recarga"".
    # I will stick to "Recarga" or similar.
    # Let's use a broader filter or the specific one if known.
    # Legacy: '876-PAGO/VENTA RECARGA-TRIVISION MONTO VARIA'
    # I'll use a LIKE filter to be safe: '%Recarga%'
    
    query = db.session.query(func.sum(Pagos.monto)).filter(
        Pagos.concepto_pago.like('%876-PAGO/VENTA RECARGA-TRIVISION MONTO VARIA%'),
        extract('year', cast(Pagos.dte, db.Date)) == now.year,
        extract('month', cast(Pagos.dte, db.Date)) == now.month
    )

    if empleado_id and empleado_id.lower() != 'none' and empleado_id.strip() != '':
        query = query.filter(func.substr(Pagos.userlogin, 1, 7) == empleado_id)

    return query.scalar() or 0
