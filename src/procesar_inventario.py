import json
import csv
import os
import sys
import ipaddress
from datetime import datetime


ARCHIVO_ENTRADA = "datos/inventario_dispositivos.json"
REPORTE_CSV = "reportes/reporte_inventario.csv"
RESUMEN_JSON = "reportes/resumen_inventario.json"


def cargar_inventario(ruta_archivo):
    """Carga el inventario desde un archivo JSON."""
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        if not isinstance(datos, list):
            raise ValueError("El archivo JSON debe contener una lista de dispositivos.")

        return datos

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_archivo}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: El archivo JSON tiene un formato inválido.")
        sys.exit(1)
    except ValueError as error:
        print(f"Error de validación: {error}")
        sys.exit(1)


def validar_dispositivo(dispositivo):
    """Valida que el dispositivo tenga los campos requeridos y una IP válida."""
    campos_requeridos = ["id", "nombre", "tipo", "ip", "estado", "ubicacion"]

    for campo in campos_requeridos:
        if campo not in dispositivo or not dispositivo[campo]:
            return False, f"Falta el campo obligatorio: {campo}"

    try:
        ipaddress.ip_address(dispositivo["ip"])
    except ValueError:
        return False, f"IP inválida: {dispositivo['ip']}"

    return True, "Dispositivo válido"


def analizar_inventario(dispositivos):
    """Procesa el inventario y genera estadísticas."""
    total = 0
    activos = 0
    mantenimiento = 0
    tipos = {}
    dispositivos_validos = []

    for dispositivo in dispositivos:
        valido, mensaje = validar_dispositivo(dispositivo)

        if not valido:
            print(f"Registro omitido: {mensaje}")
            continue

        total += 1
        dispositivos_validos.append(dispositivo)

        estado = dispositivo["estado"].lower()
        tipo = dispositivo["tipo"].lower()

        if estado == "activo":
            activos += 1
        elif estado == "mantenimiento":
            mantenimiento += 1

        tipos[tipo] = tipos.get(tipo, 0) + 1

    resumen = {
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_dispositivos_validos": total,
        "dispositivos_activos": activos,
        "dispositivos_en_mantenimiento": mantenimiento,
        "cantidad_por_tipo": tipos
    }

    return dispositivos_validos, resumen


def generar_reporte_csv(dispositivos, ruta_salida):
    """Genera un reporte CSV con los dispositivos procesados."""
    campos = ["id", "nombre", "tipo", "ip", "estado", "ubicacion"]

    with open(ruta_salida, "w", newline="", encoding="utf-8") as archivo_csv:
        escritor = csv.DictWriter(archivo_csv, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(dispositivos)


def generar_resumen_json(resumen, ruta_salida):
    """Genera un archivo JSON con el resumen del inventario."""
    with open(ruta_salida, "w", encoding="utf-8") as archivo_json:
        json.dump(resumen, archivo_json, indent=4, ensure_ascii=False)


def main():
    os.makedirs("reportes", exist_ok=True)

    dispositivos = cargar_inventario(ARCHIVO_ENTRADA)
    dispositivos_validos, resumen = analizar_inventario(dispositivos)

    generar_reporte_csv(dispositivos_validos, REPORTE_CSV)
    generar_resumen_json(resumen, RESUMEN_JSON)

    print("Procesamiento finalizado correctamente.")
    print(f"Total de dispositivos válidos: {resumen['total_dispositivos_validos']}")
    print(f"Reporte CSV generado: {REPORTE_CSV}")
    print(f"Resumen JSON generado: {RESUMEN_JSON}")


if __name__ == "__main__":
    main()
