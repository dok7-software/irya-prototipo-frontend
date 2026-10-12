# RUTA · Prototipo integral

Prototipo navegable de la app de RUTA, un marketplace de viajes compartidos entre ciudades del Perú, empezando por el corredor Lima ↔ Ica con parada en Asia. Tiene 115 pantallas móviles que unen todos los flujos diseñados:

| Flujo | Qué cubre |
|---|---|
| Navegación principal | Inicio, mis viajes, avisos y perfil del pasajero y del conductor |
| P-01 · Registro y verificación | Crear la cuenta, verificar al pasajero y habilitar al conductor |
| Perfil del conductor | Vehículo, documentos, medio de cobro y preferencias |
| P-02 · Publicación de viaje | Ruta, puntos, salida, condiciones, precio por tramo y publicación |
| P-03 · Búsqueda, reserva y pago | Del buscador al código de abordaje, con tarjeta, billetera o efectivo |
| P-12 · Acompañantes | Enlace de un solo uso para verificar a quien viaja con el titular |
| P-04 · Ejecución del viaje | Apertura con verificación facial, abordaje, SOS y confirmación de llegada |
| P-07 · Wallet del conductor | Saldo, movimientos, recargas, retiros y límites por deuda |

## Verlo

No necesita instalar nada. Abre `index.html` en el navegador y pulsa **Iniciar la demo**, o entra a cualquier pantalla desde el índice.

Para servirlo en local:

```bash
python3 -m http.server 8000
# http://localhost:8000
```

También funciona tal cual en GitHub Pages: Settings → Pages → *Deploy from a branch* → `main` / raíz.

## Estructura

```
design/            Pantallas fuente (.dc.html) y canvas.json del lienzo de diseño
app/               Pantallas navegables generadas (una por archivo) + runtime.js
index.html         Índice de todas las pantallas, agrupadas por flujo
scripts/build.py   Regenera app/ e index.html a partir de design/
```

`design/` es la fuente de verdad. Cada pantalla es un archivo `.dc.html` con su marcado, sus estados (`<sc-if>`) y una clase `Component` con la lógica de la pantalla. `app/runtime.js` es un runtime mínimo, sin dependencias, que evalúa esa lógica, resuelve los estados y conecta los botones y campos. Los enlaces entre pantallas se mantienen.

Después de cambiar algo en `design/`:

```bash
python3 scripts/build.py
```

El script también avisa si algún enlace apunta a una pantalla que no existe.

## Datos de la demo

Todos los flujos comparten la misma historia, para que los montos y nombres cuadren de una pantalla a otra.

- **Viaje del viernes 9 de octubre:** Lima, Jockey Plaza, a las 06:30 → Asia, grifo Primax, entre 07:30 y 08:15 → Ica, Plaza de Armas, a las 11:00.
- **Conductor:** Marco Salazar (4.9 · 128 viajes), en un Toyota Yaris 2019 plata, placa AKV-482.
- **Precios por asiento:** el pasajero paga el precio del conductor más el servicio de RUTA, que es el 18 % con IGV incluido.

  | Tramo | Recibe el conductor | Paga el pasajero |
  |---|---|---|
  | Lima → Ica | S/ 25.00 | S/ 29.50 |
  | Lima → Asia | S/ 10.00 | S/ 11.80 |
  | Asia → Ica | S/ 15.00 | S/ 17.70 |

- **Asientos:**
  - Asientos 1 y 2: Lucía Rojas (titular) y Diego Rojas (acompañante), de Lima a Ica, con tarjeta. Pagan S/ 59.00 menos cupones de S/ 7.50 y S/ 5.00, es decir S/ 46.50.
  - Asiento 3: Ana Torres de Lima a Asia (no se presenta y queda marcada como ausente) y Rosa Vilcapoma de Asia a Ica, que paga S/ 17.70 en efectivo.
- **Wallet del conductor:** S/ 124.50.

## Notas

- Es un prototipo de diseño: no hay backend, pagos ni verificación reales. Algunos botones marcados como "Siguiente" existen solo para que la demo avance de forma fluida.
- Las tipografías (IBM Plex Sans y Mono) se cargan desde Google Fonts. Sin conexión se usa la fuente del sistema.
