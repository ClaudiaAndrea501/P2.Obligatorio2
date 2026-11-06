# Orbita Verde: Rescate estelar

Un juego corto de supervivencia y reciclaje controlado con la cámara. La nave sigue un marcador verde y atraviesa cuatro niveles que representan la mañana, el mediodía, la tarde y la noche. El cielo y la cantidad de nubes cambian en cada nivel.

## Requisitos

- Python 3.10 o posterior.
- Una webcam habilitada y un objeto verde (por ejemplo, una hoja de papel).
- Dependencias instaladas desde `requirements.txt`.

## Instalacion y ejecucion

Desde esta carpeta, ejecuta:

```bash
python -m pip install -r requirements.txt
python main.py
```

La camara debe estar conectada y tener permiso de uso. Si el sistema usa otra cámara, cambia `CAMERA_INDEX` en `ajustes.py`.

## Como jugar

1. Coloca una hoja u objeto verde intenso frente a la cámara; que ocupe una zona visible y tenga buena iluminación.
2. Mueve el objeto para guiar la nave. La imagen se espeja para que el movimiento se sienta natural.
3. Atrapa las botellas traslúcidas verdes con tapa verde y evita las pilas usadas. Tocar una pila resta una vida. En la vida real, las pilas usadas se llevan a un punto de recepción de pilas para que reciban un tratamiento separado; no van con las botellas ni al contenedor común.
4. Para avanzar necesitas juntar 6 botellas por la mañana, 12 al mediodía, 18 por la tarde y 24 por la noche. Tienes tres vidas y 75 segundos para completar los cuatro niveles.
5. Al ganar o perder, escribe tu nombre y presiona `Enter`. Se guardará tu puntaje total de botellas y se mostrará el ranking local de los 10 mejores resultados.
6. En la tabla de ranking, presiona `R` para volver a jugar sin cerrar la ventana.
7. Si aparece el aviso de deteccion, acerca el objeto verde, mejora la iluminacion y evita que otros objetos verdes queden dentro del encuadre.
8. Presiona `Esc` para salir de la pantalla completa.

El ranking se guarda en `ranking.json` dentro de esta carpeta y persiste entre partidas en la misma computadora.

La musica no es necesaria: el juego incluye dos efectos de sonido, uno para recoger botellas y otro para los impactos.

## Controles y camara

La posicion del marcador verde controla la mano que ves en pantalla. El juego muestra una mano ilustrada; la camara sigue detectando un objeto verde, no reconoce una mano real. OpenCV detecta el color en `vision.py`, que devuelve una coordenada o `None`; el juego no manipula cuadros de video. Los rangos HSV y parametros editables estan en `ajustes.py`.

## Estructura

- `main.py`: bucle principal, reglas, objetos y dibujo.
- `vision.py`: apertura, lectura, espejo y deteccion de la camara.
- `ajustes.py`: colores y parametros del juego y del detector.
- `ranking.json`: se crea al terminar la primera partida y guarda los mejores puntajes locales.
- `assets/sounds/`: efectos de sonido.
- `informe.pdf`: informe y afiche.

## GitHub

Enlace al repositorio: [github.com/ClaudiaAndrea501/P2.Obligatorio2](https://github.com/ClaudiaAndrea501/P2.Obligatorio2)
