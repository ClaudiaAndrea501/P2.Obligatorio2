# Orbita Verde: Rescate estelar

Un juego corto de supervivencia y reciclaje controlado con la cámara. El elemento verde que el jugador sostiene mueve el control invisible del juego, sobre la imagen de la cámara que ocupa toda la pantalla. La partida atraviesa cuatro niveles que representan la mañana, el mediodía, la tarde y la noche.

## Requisitos

- Python 3.10 o posterior.
- Una webcam habilitada y un objeto verde vivo (por ejemplo, una tapa) visible frente a la cámara.
- Dependencias instaladas desde `requirements.txt`.

## Instalacion y ejecucion

Desde esta carpeta, ejecuta:

```bash
python -m pip install -r requirements.txt
python main.py
```

La camara debe estar conectada y tener permiso de uso. Si el sistema usa otra cámara, cambia `CAMERA_INDEX` en `ajustes.py`.

## Como jugar

1. La imagen espejada de la cámara ocupa toda la pantalla. Los objetos del juego y los puntajes aparecen encima, sin cielo ni nubes dibujados.
2. Sostén un elemento verde frente a la cámara, con buena luz y separado de otros objetos verdes. Mueve ese elemento para controlar el juego; no se dibuja una tapa ni un cursor en la pantalla.
3. Atrapa las botellas traslúcidas verdes con tapa verde y evita las pilas usadas. Tocar una pila resta una vida. En la vida real, las pilas usadas se llevan a un punto de recepción de pilas para que reciban un tratamiento separado; no van con las botellas ni al contenedor común.
4. Para avanzar necesitas juntar 6 botellas por la mañana, 12 al mediodía, 18 por la tarde y 24 por la noche. Tienes tres vidas y 75 segundos para completar los cuatro niveles.
5. Al ganar o perder, escribe tu nombre y presiona `Enter`. Se guardará tu puntaje total de botellas y se mostrará el ranking local de los 10 mejores resultados.
6. En la tabla de ranking, presiona `R` para volver a jugar sin cerrar la ventana.
7. Si aparece el aviso de detección, acerca el objeto verde, mejora la iluminación y evita otros objetos verdes en el encuadre.
8. Presiona `Esc` para salir de la pantalla completa.

El ranking se guarda en `ranking.json` dentro de esta carpeta y persiste entre partidas en la misma computadora.

La musica no es necesaria: el juego incluye dos efectos de sonido, uno para recoger botellas y otro para los impactos.

## Controles y camara

`vision.py` espeja el cuadro y detecta el color verde en HSV. El centro del objeto detectado mueve el control invisible; la imagen de cámara, sin tintes ni escenarios dibujados, ocupa toda la pantalla. El seguimiento elige la mancha verde más probable y prioriza la que continúa cerca de la posición anterior. Si no encuentra el objeto, devuelve `None` y el control queda quieto.

## Estructura

- `main.py`: bucle principal, reglas, objetos y dibujo.
- `vision.py`: apertura, lectura, espejo y seguimiento del objeto verde con OpenCV.
- `ajustes.py`: colores y parámetros del juego y del detector de color.
- `ranking.json`: se crea al terminar la primera partida y guarda los mejores puntajes locales.
- `assets/sounds/`: efectos de sonido.
- `informe.pdf`: informe y afiche.

## GitHub

Enlace al repositorio: [github.com/ClaudiaAndrea501/P2.Obligatorio2](https://github.com/ClaudiaAndrea501/P2.Obligatorio2)
