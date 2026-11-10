import hashlib
import os
import pandas as pd


def calcular_sha256(ruta_fichero):
  """Calcula el hash SHA-256 de un archivo en bloques binarios."""
  sha = hashlib.sha256()
  with open(ruta_fichero, "rb") as f:
    for bloque in iter(lambda: f.read(4096), b""):
      sha.update(bloque)
  return sha.hexdigest()


def sanear_telemetria(input_path, output_path):
  print(f"[+] Calculando SHA-256 de entrada ({input_path})...")
  hash_origen = calcular_sha256(input_path)
  print(f"    Hash Origen: {hash_origen}")

  # Carga de datos
  df = pd.read_csv(input_path)
  filas_iniciales = len(df)

  # 1. Deduplicación
  df = df.drop_duplicates()

  # 2. Eliminar nulos en campos clave (temp_celsius, peso_kg, destino)[cite: 6]
  df = df.dropna(subset=["temp_celsius", "peso_kg", "destino"])

  # 3. Filtrar incongruencias lógicas de negocio[cite: 6]
  df = df[df["peso_kg"] > 0]  # Sin pesos negativos
  df = df[df["temp_celsius"] <= 50.0]  # Sin lecturas extremas de frío
  df = df[df["estado_envio"] != "DESCONOCIDO_ERROR"]  # Estados válidos

  filas_finales = len(df)
  print(
      f"[+] Registros procesados: {filas_iniciales} -> {filas_finales}"
      f" (Eliminados: {filas_iniciales - filas_finales})"
  )

  # Guardar archivo limpio
  df.to_csv(output_path, index=False)

  hash_destino = calcular_sha256(output_path)
  print(f"[+] Archivo depurado guardado en: {output_path}")
  print(f"    Hash Limpio: {hash_destino}")


if __name__ == "__main__":
  # Obtiene la ruta absoluta de la carpeta raíz (laboratorio2)
  RUTA_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
  RUTA_RAIZ = os.path.dirname(RUTA_SCRIPTS)

  fichero_origen = os.path.join(RUTA_RAIZ, "datos", "telemetria_envios.csv")
  fichero_destino = os.path.join(RUTA_RAIZ, "datos", "telemetria_limpia.csv")
  sanear_telemetria(fichero_origen, fichero_destino)
