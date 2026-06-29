import wx

# Tema compartido para toda la aplicación.
# Puede ser "Claro" u "Oscuro".
tema_actual = "Claro"


def establecer_tema(tema):
    # Cambia el tema activo si el valor es válido.
    global tema_actual
    if tema in ("Claro", "Oscuro"):
        tema_actual = tema


def obtener_tema():
    # Devuelve el tema que está seleccionado en este momento.
    return tema_actual


def _colores_del_tema(tema=None):
    # Devuelve (fondo, texto) según el tema.
    if tema is None:
        tema = tema_actual
    if tema == "Oscuro":
        return wx.Colour(0, 0, 0), wx.Colour(255, 255, 255)
    return wx.Colour("#FFFFFF"), wx.Colour(0, 0, 0)


def aplicar_tema_a_ventana(frame):
    # Aplica el tema actual a la ventana principal y su panel de contenido.
    color_fondo, color_texto = _colores_del_tema()

    frame.SetBackgroundColour(color_fondo)

    panel = getattr(frame, "panel_contenido", None)
    if panel is None:
        # Si no hay panel de contenido, solo refrescamos la ventana.
        frame.Refresh()
        return

    panel.SetBackgroundColour(color_fondo)

    dvc = getattr(panel, "dvc", None)
    if dvc is not None:
        dvc.SetBackgroundColour(color_fondo)
        dvc.SetForegroundColour(color_texto)

    for control in panel.GetChildren():
        if hasattr(control, "SetForegroundColour"):
            control.SetForegroundColour(color_texto)

    panel.Refresh()
    panel.Layout()
    frame.Refresh()
