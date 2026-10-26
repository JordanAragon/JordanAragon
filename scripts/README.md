# Cómo se genera el perfil

Todo lo que se ve en el perfil son imágenes SVG en `assets/`, en versión clara y oscura (el README elige una según el tema de GitHub del visitante). Se generan con `scripts/build.py` a partir de `scripts/datos.py`.

- **Cambiar un texto, un proyecto o el stack:** editar `scripts/datos.py` y subir el cambio a `main`. La acción «Perfil» regenera las imágenes sola.
- **Correrlo en local:** `pip install fonttools brotli` y `python3 scripts/build.py`. Con `GITHUB_TOKEN` también actualiza la tarjeta de actividad.
- **Actividad:** la acción «Perfil» corre cada día y actualiza contribuciones, racha y lenguajes de los repos públicos.
- **Serpiente:** la acción «Serpiente de contribuciones» la dibuja cada día en la rama `output`.

Recursos en `scripts/recursos/`:

- Inter y JetBrains Mono (licencia OFL, `LICENSE.txt`). Cada SVG lleva incrustadas solo las letras que usa.
- Íconos de [Simple Icons](https://simpleicons.org) (CC0).
- `foto.jpg` (recorte de la foto) y `foto-hero.webp` (la versión que va en el encabezado, 880 × 960).
- `metricas.json`: anchos de letra para medir y partir textos.
