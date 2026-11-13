# Orbita Verde: Rescate estelar

Un juego de reciclaje controlado con la cámara. El jugador mueve la mano sobre la imagen de la cámara, que ocupa toda la pantalla. La partida tiene ocho niveles: en cada uno hay que aplastar una cantidad determinada de una botella objetivo.

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

1. La imagen espejada de la cámara y el juego se ajustan a toda la pantalla, sin franjas negras laterales. La información aparece en una franja superior fina, blanca y opaca, con textos verdes distribuidos en filas parejas.
2. Abre la mano para mover el punto de contacto y ciérrala para aplastar la botella que tocaste.
3. Cada nivel indica la botella objetivo con una imagen y su nombre. Aplastar una botella de otro color resta una vida; tienes tres vidas para toda la partida.
   Aparecen botellas de los ocho colores en cada nivel; la botella objetivo aparece con más frecuencia.
4. Completa los ocho niveles antes de que se termine el tiempo indicado en cada nivel:
   - Agua sin gas (verde): 6 botellas en 32 segundos.
   - Agua con gas (verde con tapa azul): 6 en 32 segundos.
   - Sabor limón (beige): 8 en 38 segundos.
   - Sabor ananá (amarillo): 10 en 43 segundos.
   - Sabor pomelo rosado: 12 en 48 segundos.
   - Sabor manzana (marrón claro): 14 en 53 segundos.
   - Sabor frutilla (rojo): 16 en 58 segundos.
   - Sabor naranja: 18 en 63 segundos.
5. Si tu puntaje entra entre los cinco mejores, escribe tu nombre y presiona `Enter` para guardarlo. Si no entra, verás el ranking y tu puntaje sin tener que escribir tu nombre.
6. Pulsa la copa de la franja superior para consultar el ranking durante la partida; la partida queda pausada mientras lo ves. Vuelve a pulsar la copa para regresar.
7. Usa el botón de pausa de la franja superior o la tecla `P` para pausar y reanudar.
8. En el ranking final, presiona `R` para volver a jugar sin cerrar la ventana.
9. Si aparece el aviso de detección, mejora la iluminación y coloca la mano completa frente a la cámara.
10. Presiona `Esc` para salir de la pantalla completa.

El ranking se guarda en `ranking.json` dentro de esta carpeta y persiste entre partidas en la misma computadora.

La música no es necesaria: el juego incluye efectos de sonido para aplastar botellas correctas y equivocadas.

## Controles y camara

`vision.py` usa MediaPipe para detectar la mano y reconocer si los dedos están extendidos o cerrados, sin depender del color. La palma mueve el punto de contacto; hay que tocar la botella con la mano abierta y cerrar la mano para aplastarla. El modelo está incluido en `assets/models/hand_landmarker.task`. La imagen de cámara ocupa toda la pantalla.

## Estructura

- `main.py`: bucle principal, reglas, objetos y dibujo de las ocho variantes de botella.
- `vision.py`: apertura de la cámara y detección de posición y gesto de la mano.
- `ajustes.py`: parámetros del juego y de la cámara.
- [Catálogo visual de botellas](assets/botellas_catalogo.png): las ocho botellas en versiones normal y aplastada.
- `assets/models/hand_landmarker.task`: modelo de detección de manos de MediaPipe.
- `ranking.json`: se crea al terminar la primera partida y guarda los mejores puntajes locales.
- `assets/sounds/`: efectos de sonido.
- `informe.pdf`: informe y afiche.

## GitHub

Enlace al repositorio: [github.com/ClaudiaAndrea501/P2.Obligatorio2](https://github.com/ClaudiaAndrea501/P2.Obligatorio2)
