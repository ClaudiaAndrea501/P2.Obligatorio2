# Misión Reciclaje: Botellas

Un juego de reciclaje controlado con la cámara. El jugador compacta botellas con el dedo índice sobre la imagen de la cámara, que ocupa toda la pantalla. La partida tiene ocho niveles: en cada uno hay que compactar una cantidad determinada de una botella objetivo.

## Requisitos

- Python 3.10 o posterior.
- Una webcam habilitada que muestre la mano del jugador.
- Dependencias instaladas desde `requirements.txt`.

## Instalación y ejecución

Desde esta carpeta, ejecuta:

```bash
python -m pip install -r requirements.txt
python main.py
```

La cámara debe estar conectada y tener permiso de uso. Si el sistema usa otra cámara, cambia `CAMERA_INDEX` en `ajustes.py`. El juego solicita video a 1280 x 720 para mejorar la nitidez; la resolución efectiva depende de lo que admita la webcam. La imagen se muestra directamente a resolución de pantalla y sin filtros de suavizado.

## Instrucciones

1. Pulsa **JUGAR**. Antes de cada nivel verás la botella objetivo, la cantidad que debes compactar y el tiempo disponible.
2. Extiende solo el índice, cierra los otros dedos y pasa la punta sobre la botella objetivo. Compactar otra botella resta una vida; tienes tres.
3. Completa los ocho niveles antes de que se agote el tiempo. El objetivo y el progreso aparecen en pantalla.
4. Usa el botón de pausa o `P` para pausar. Pulsa la copa para consultar el ranking; vuelve a pulsarla para regresar.
5. Si entras entre los cinco mejores, escribe tu nombre y presiona `Enter`. En el ranking final, `R` inicia otra partida y `Esc` sale del juego.

El ranking se guarda en `ranking.json` dentro de esta carpeta y persiste entre partidas en la misma computadora.

El juego incluye efectos de sonido para compactar botellas correctas y equivocadas.

## Mejorar la detección

- **Luz:** usa iluminación pareja de frente; evita el contraluz y las sombras fuertes.
- **Fondo:** elige uno simple, sin objetos que se confundan con la mano.
- **Distancia:** empieza a unos 50–100 cm y ajusta para que la mano completa se vea con claridad, sin quedar cortada.
- **Postura:** mantén la mano frente a la cámara.

## Estructura

- `main.py`: bucle principal, reglas, objetos y dibujo de las ocho variantes de botella.
- `vision.py`: apertura de la cámara y detección de posición y gesto de la mano.
- `ajustes.py`: parámetros del juego y de la cámara.
- [Catálogo visual de botellas](assets/botellas_catalogo.png): las ocho botellas en versiones normal y compactada.
- `assets/models/hand_landmarker.task`: modelo de detección de manos de MediaPipe.
- `ranking.json`: se crea al terminar la primera partida y guarda los mejores puntajes locales.
- `assets/sounds/`: efectos de sonido.
- `informe.pdf`: informe y afiche.

## GitHub

Enlace al repositorio: [github.com/ClaudiaAndrea501/P2.Obligatorio2](https://github.com/ClaudiaAndrea501/P2.Obligatorio2)
