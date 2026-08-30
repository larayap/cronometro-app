#!/usr/bin/env python3
"""Genera los assets de icono de la app desde los SVG de arte.

Windows no escala un icono: elige del `.ico` la imagen cuyo tamaño coincide con
la ranura que va a pintar (16 px en la lista de descargas, 24 en la barra de
tareas, 32 y 48 en el escritorio, 256 en la vista de iconos extra grandes) y
solo interpola cuando no encuentra ninguna. Por eso el `.ico` lleva las nueve
imágenes rasterizadas de forma independiente en vez de una sola grande.

Cada rango de tamaño usa el arte que le corresponde (ver REPARTO): el maestro
para 64 px y más, y las dos variantes de `build/icons/` para lo que queda, donde
los trazos del maestro caerían por debajo del píxel.

El rasterizado lo hace Chromium en modo headless —es el único motor SVG
disponible acá y el mismo que dibuja la ventana de la app—, y el `.ico` se
arma a mano porque Pillow reescala internamente a partir de una sola imagen,
que es justo lo que este script evita.

Uso:
    python3 build/icons/generate-icons.py

Requiere: Chromium (`chromium` o `chromium-browser`) y Pillow.
"""

import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
ART_MASTER = REPO / 'public' / 'icon-app.svg'
ART_MEDIUM = REPO / 'build' / 'icons' / 'icon-app-medium.svg'
ART_SMALL = REPO / 'build' / 'icons' / 'icon-app-small.svg'

# Tamaño de cada imagen del .ico y el arte del que se rasteriza. Los tres cortes
# están justificados en el comentario de cabecera de cada SVG.
REPARTO = [
    (16, ART_SMALL),
    (20, ART_SMALL),
    (24, ART_SMALL),
    (32, ART_MEDIUM),
    (40, ART_MEDIUM),
    (48, ART_MEDIUM),
    (64, ART_MASTER),
    (128, ART_MASTER),
    (256, ART_MASTER),
]

# Lado al que se rasteriza cada arte antes de reducir al tamaño final. Es
# múltiplo de los nueve tamaños del reparto salvo 40, y lo bastante grande para
# que la reducción Lanczos promedie varios píxeles de origen por cada uno de
# destino, que es lo que da el borde limpio.
LADO_RASTERIZADO = 1024

# El icono de la bandeja es un PNG aparte porque Electron lo pide así en
# `Tray`. La variante @2x la toma solo cuando el escritorio corre escalado.
TRAY_PNG = REPO / 'public' / 'img' / 'icon-app.png'
TRAY_PNG_2X = REPO / 'public' / 'img' / 'icon-app@2x.png'
TRAY_TAMANOS = [(TRAY_PNG, 32, ART_MEDIUM), (TRAY_PNG_2X, 64, ART_MASTER)]

ICO_SALIDA = REPO / 'public' / 'icon-app.ico'

# Por debajo de este tamaño la imagen va como BMP dentro del .ico. Windows lee
# PNG embebido desde Vista, pero varias superficies del shell siguen esperando
# BMP en las ranuras chicas y ante la duda dibujan el icono genérico.
UMBRAL_BMP = 48


def buscar_chromium() -> str:
    for nombre in ('chromium', 'chromium-browser', 'google-chrome', 'chrome'):
        ruta = shutil.which(nombre)
        if ruta:
            return ruta
    sys.exit('No se encontró Chromium. Instalalo o ajustá buscar_chromium().')


def rasterizar(chromium: str, svg: Path, destino: Path, lado: int) -> Image.Image:
    """Rasteriza un SVG a `lado`x`lado` px y devuelve la imagen resultante."""
    pagina = destino / f'{svg.stem}.html'
    salida = destino / f'{svg.stem}.png'
    # El <img> lleva el lado fijo para que Chromium rasterice a esa resolución
    # en vez de escalar después el dibujo del viewBox.
    pagina.write_text(
        '<style>html,body{margin:0;padding:0}'
        f'img{{display:block;width:{lado}px;height:{lado}px}}</style>'
        f'<img src="{svg.as_uri()}">',
        encoding='utf-8',
    )
    subprocess.run(
        [
            chromium, '--headless', '--no-sandbox', '--disable-gpu',
            '--allow-file-access-from-files', '--hide-scrollbars',
            '--force-device-scale-factor=1',
            f'--window-size={lado},{lado}',
            f'--screenshot={salida}',
            pagina.as_uri(),
        ],
        check=True,
        capture_output=True,
    )
    if not salida.exists():
        sys.exit(f'Chromium no escribió {salida} al rasterizar {svg.name}.')
    with Image.open(salida) as im:
        return im.convert('RGBA')


def reducir(base: Image.Image, lado: int) -> Image.Image:
    return base.resize((lado, lado), Image.LANCZOS)


def codificar_bmp(imagen: Image.Image) -> bytes:
    """Serializa la imagen como el BMP sin cabecera de archivo que espera un .ico.

    Son tres bloques: un BITMAPINFOHEADER cuyo alto se declara al doble porque
    cuenta las dos máscaras, los píxeles BGRA de abajo hacia arriba, y una
    máscara AND de 1 bit por píxel que queda en cero (el canal alfa ya resuelve
    la transparencia) pero que igual va porque el formato la exige.
    """
    lado = imagen.width
    cabecera = struct.pack(
        '<IiiHHIIiiII',
        40,            # tamaño de la cabecera
        lado,          # ancho
        lado * 2,      # alto: imagen + máscara AND
        1,             # planos
        32,            # bits por píxel
        0,             # sin compresión
        0,             # tamaño de la imagen (opcional en BI_RGB)
        0, 0,          # resolución horizontal y vertical
        0, 0,          # colores usados e importantes
    )
    pixeles = bytearray()
    datos = imagen.load()
    for y in range(lado - 1, -1, -1):
        for x in range(lado):
            r, g, b, a = datos[x, y]
            pixeles += bytes((b, g, r, a))
    # Cada fila de la máscara se alinea a 4 bytes.
    bytes_por_fila = ((lado + 31) // 32) * 4
    mascara = bytes(bytes_por_fila * lado)
    return cabecera + bytes(pixeles) + mascara


def codificar_png(imagen: Image.Image) -> bytes:
    import io
    buffer = io.BytesIO()
    imagen.save(buffer, format='PNG', optimize=True)
    return buffer.getvalue()


def escribir_ico(imagenes: list[tuple[int, Image.Image]], destino: Path) -> None:
    cuerpos = [
        codificar_bmp(im) if lado <= UMBRAL_BMP else codificar_png(im)
        for lado, im in imagenes
    ]
    # Las entradas del directorio son de largo fijo, así que el primer cuerpo
    # arranca justo después de todas.
    offset = 6 + 16 * len(imagenes)
    directorio = bytearray(struct.pack('<HHH', 0, 1, len(imagenes)))
    for (lado, _), cuerpo in zip(imagenes, cuerpos):
        directorio += struct.pack(
            '<BBBBHHII',
            lado if lado < 256 else 0,  # 256 se codifica como 0
            lado if lado < 256 else 0,
            0,          # paleta: ninguna
            0,          # reservado
            1,          # planos
            32,         # bits por píxel
            len(cuerpo),
            offset,
        )
        offset += len(cuerpo)
    destino.write_bytes(bytes(directorio) + b''.join(cuerpos))


def main() -> None:
    chromium = buscar_chromium()
    # El temporal va dentro del repo: cuando Chromium viene empaquetado como
    # snap o flatpak queda confinado y no escribe el screenshot en /tmp.
    with tempfile.TemporaryDirectory(dir=REPO, prefix='.icongen-') as tmp:
        temporal = Path(tmp)
        # Un rasterizado por arte; de ahí salen todos sus tamaños.
        bases = {
            svg: rasterizar(chromium, svg, temporal, LADO_RASTERIZADO)
            for svg in {ART_MASTER, ART_MEDIUM, ART_SMALL}
        }

        imagenes = [(lado, reducir(bases[svg], lado)) for lado, svg in REPARTO]
        escribir_ico(imagenes, ICO_SALIDA)
        print(f'{ICO_SALIDA.relative_to(REPO)} — {len(imagenes)} tamaños: '
              + ', '.join(str(lado) for lado, _ in imagenes))

        for destino, lado, svg in TRAY_TAMANOS:
            reducir(bases[svg], lado).convert('RGB').save(destino, optimize=True)
            print(f'{destino.relative_to(REPO)} — {lado}x{lado}')


if __name__ == '__main__':
    main()
