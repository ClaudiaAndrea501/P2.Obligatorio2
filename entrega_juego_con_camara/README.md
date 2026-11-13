# Orbita Verde: Rescate estelar

Un juego corto de supervivencia y reciclaje controlado con la cámara. El jugador mueve la mano sobre la imagen de la cámara, que ocupa toda la pantalla. La partida atraviesa cuatro niveles que representan la mañana, el mediodía, la tarde y la noche.

## Requisitos

- Python 3.10 o posterior.
- Una webcam habilitada que muestre la mano del jugador.
- Dependencias instaladas desde `requirements.txt`.

## Instalacion y ejecucion

Desde esta carpeta, ejecuta:

```bash
python -m pip install -r requirements.txt
python main.py
```

La camara debe estar conectada y tener permiso de uso. Si el sistema usa otra cámara, cambia `CAMERA_INDEX` en `ajustes.py`. El juego solicita video a 1280 x 720 para mejorar la nitidez; la resolución efectiva depende de lo que admita la webcam.

## Como jugar

1. La imagen espejada de la cámara ocupa toda la pantalla. Los objetos del juego y los puntajes aparecen encima, sin cielo ni nubes dibujados.
2. Abre la mano para mover el punto de contacto. Toca una botella con la mano abierta y cierra la mano para aplastarla; no importa el color de la mano.
3. Las botellas aplastadas suman puntos. Tocar una pila con la mano abierta resta una vida. En la vida real, las pilas usadas se llevan a un punto de recepción de pilas para que reciban un tratamiento separado; no van con las botellas ni al contenedor común.
4. Para avanzar necesitas juntar 6 botellas por la mañana, 12 al mediodía, 18 por la tarde y 24 por la noche. Tienes tres vidas y 75 segundos para completar los cuatro niveles.
5. Al ganar o perder, escribe tu nombre y presiona `Enter`. Se guardará tu puntaje total de botellas y se mostrará el ranking local de los 5 mejores resultados.
6. En la tabla de ranking, presiona `R` para volver a jugar sin cerrar la ventana.
7. Si aparece el aviso de detección, mejora la iluminación y coloca la mano completa frente a la cámara.
8. Presiona `Esc` para salir de la pantalla completa.

El ranking se guarda en `ranking.json` dentro de esta carpeta y persiste entre partidas en la misma computadora.

La musica no es necesaria: el juego incluye dos efectos de sonido, uno para recoger botellas y otro para los impactos.

## Controles y camara

`vision.py` usa MediaPipe para detectar la mano y reconocer si los dedos están extendidos o cerrados, sin depender del color. La palma mueve el punto de contacto; hay que tocar la botella con la mano abierta y cerrar la mano para aplastarla. El modelo está incluido en `assets/models/hand_landmarker.task`. La imagen de cámara ocupa toda la pantalla.

## Estructura

- `main.py`: bucle principal, reglas, objetos y dibujo.
- `vision.py`: apertura de la cámara y detección de posición y gesto de la mano.
- `ajustes.py`: parámetros del juego y de la cámara.
- `assets/models/hand_landmarker.task`: modelo de detección de manos de MediaPipe.
- `ranking.json`: se crea al terminar la primera partida y guarda los mejores puntajes locales.
- `assets/sounds/`: efectos de sonido.
- `informe.pdf`: informe y afiche.

## GitHub

Enlace al repositorio: [github.com/ClaudiaAndrea501/P2.Obligatorio2](https://github.com/ClaudiaAndrea501/P2.Obligatorio2)
