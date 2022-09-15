from db import connection
from datetime import datetime, timedelta

columns = {
  'numero_compania': 0, 
  'mes': 1, 
  'numero_poliza': 2, 
  'consecutivo_detalle_poliza': 3, 
  'fecha_movimiento': 4, 
  'cuenta': 5, 
  'auxiliar_1': 6, 
  'auxiliar_2': 7,
  'auxiliar_3': 8,
  'concepto_detalle_poliza': 9,
  'importe_cargo': 10,
  'importe_abono': 11,
  'estatus': 12,
  'estatus_origen': 13,
  'descripcion_cuenta': 14,
  'tipo_cambio': 15,
  'numero_grupo': 16,
  'numero_regla': 17
}

headers = {
    'tipoPoliza': '3', 
    'clase': '1', 
    'idDiario': '0', 
    'impresa': '1', 
    'ajuste': '1', 
    'guid': '0', 
    'P': 'P', 
    'SisOrig': '11'
}

query = connection.cursor()

query.execute('SELECT fecha_movimiento FROM CONTAB_DETALLE_POLIZAS ORDER BY fecha_movimiento limit 1')
startDate = query.fetchone()[0]
fechaInicio = startDate

endDate = datetime(2014, 12, 31)

text = []

def formatString(string, fill, align, width):
    return f'{string:{fill}{align}{width}}'

while (startDate <= endDate):
    query.execute('SELECT * FROM CONTAB_DETALLE_POLIZAS WHERE date(fecha_movimiento) = %(date)s', { 'date': startDate.date() })
    movimientos = query.fetchall()

    if (len(movimientos) < 1):
        startDate += timedelta(days=1)
        continue

    headers['folio'] = '0' + '{:02d}'.format(startDate.day)
    headers['concepto'] = f'Poliza capvital del día {startDate.date()}'
    headers['fecha'] = startDate.date().strftime('%Y%m%d')

    text.append(
        formatString(headers['P'], ' ', '<', 3) + 
        formatString(headers['fecha'], ' ', '<', 12) + 
        formatString(headers['tipoPoliza'], ' ', '<',8) + 
        formatString(headers['folio'], ' ', '<', 4) +
        formatString(headers['clase'], ' ', '<', 13) +
        formatString(headers['concepto'], ' ', '<', 100) +
        formatString(headers['SisOrig'], ' ', '<', 3) +
        formatString(headers['impresa'], ' ', '<', 2) +
        headers['ajuste']
    )

    for movimiento in movimientos:
        tipoCartera = 'activa' if movimiento[columns['importe_cargo']] is not None and abs(movimiento[columns['importe_cargo']]) > 0 else 'pasiva'
        tipoMovimiento = 0 if tipoCartera == 'activa' else 1
        importe = movimiento[columns['importe_cargo']] if tipoCartera == 'activa' else movimiento[columns['importe_abono']]
        importe = importe if importe is not None else 0

        text.append(
            formatString('M1', ' ', '<', 3) +
            formatString(movimiento[columns['cuenta']], ' ', '<', 31) +
            formatString(tipoCartera, ' ', '<', 21) +
            formatString(tipoMovimiento, ' ', '<', 2) +
            formatString(importe, ' ', '<', 21) +
            formatString('0', ' ', '<', 11) +
            formatString('0.0', ' ', '<', 21) +
            formatString(movimiento[columns['concepto_detalle_poliza']], ' ', '<', 101)
        )

    startDate += timedelta(days=1)

with open(f'/mnt/c/Users/david/Desktop/Contpaq+{fechaInicio.date()}+{endDate.date()}.txt', 'w') as txt_file:
    for line in text:
        txt_file.write(line + "\n")
