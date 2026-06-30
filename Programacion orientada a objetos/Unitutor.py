#Login - Usuario y contraseña
#WxPython - Interfaz Grafica
#Programacion orientada a objetos
#AboutBox, AdvancedSplash, Menu, PrintDialog

import wx.lib.agw.aquabutton as AB
import wx
import wx.lib.agw.advancedsplash as AS
import os
import sys
from Backend import modtutores
try:
    dirName = os.path.dirname(os.path.abspath(__file__))
except:
    dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

bitmapDir = os.path.join(dirName, 'bitmaps')

class MiPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.color_fondo()
    

#Botones de iniciar sesion y cerrar
        self.boton = AB.AquaButton(self, -1, label='Iniciar Sesion')
        self.botonCerrar = AB.AquaButton(self, label='Cerrar')
        self.boton.SetBackgroundColour(wx.Colour("#2E86C1"))
        self.boton.SetHoverColour(wx.Colour("#1B4F72"))
        self.boton.SetFocusColour(wx.Colour("#3498DB"))
        self.boton.SetForegroundColour(wx.Colour("#FFFFFF"))
        self.botonCerrar.SetBackgroundColour(wx.Colour("#E74C3C"))
        self.botonCerrar.SetHoverColour(wx.Colour("#B03A2E"))
        self.botonCerrar.SetFocusColour(wx.Colour("#EC7063"))
        self.botonCerrar.SetForegroundColour(wx.Colour("#FFFFFF"))
        self.boton.Bind(wx.EVT_BUTTON, self.on_boton_click)
        self.botonCerrar.Bind(wx.EVT_BUTTON, self.on_boton_cerrar)

        # Logo centrado en el panel y redimensionado manteniendo proporción
        logo_img = wx.Image('Logo/Unitutor.png', wx.BITMAP_TYPE_PNG)
        ancho_original, alto_original = logo_img.GetSize()
        max_ancho, max_alto = 150, 150
        if ancho_original > alto_original:
            nuevo_ancho = max_ancho
            nuevo_alto = int(max_ancho * alto_original / ancho_original)
        else:
            nuevo_alto = max_alto
            nuevo_ancho = int(max_alto * ancho_original / alto_original)
        logo_img = logo_img.Scale(nuevo_ancho, nuevo_alto, wx.IMAGE_QUALITY_HIGH)
        logo_bmp = wx.Bitmap(logo_img)
        self.logo_ctrl = wx.StaticBitmap(self, bitmap=logo_bmp)

    #Logo pequeño para el borde de ventana al lado de titulo
        logo_pequeño = wx.Image('Logo/Unitutor.png', wx.BITMAP_TYPE_PNG)
        logo_pequeño = logo_pequeño.Scale(32, 32, wx.IMAGE_QUALITY_HIGH)
        logo_pequeño_bmp = wx.Bitmap(logo_pequeño)
        self.GetTopLevelParent().SetIcon(wx.Icon(logo_pequeño_bmp))

    # Usuario y Contraseña
        self.usuario = wx.TextCtrl(self, size=(220, -1))
        self.contraseña = wx.TextCtrl(self, style=wx.TE_PASSWORD, size=(220, -1))
    #Boton iniciar sesion con aquaButton (creado arriba)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.logo_ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.BOTTOM, 15) #Fija el logo arriba con margen

        sizer.Add(wx.StaticText(self, label='Usuario:'), 0, wx.CENTRE, 5) #Posicion de texto Usuario
        sizer.Add(self.usuario, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer.Add(wx.StaticText(self, label='Contraseña:'), 0, wx.CENTRE, 5) #Posicion de texto Contraseña
        sizer.Add(self.contraseña, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

#Ubicacion de botones iniciar sesion y cerrar | CENTRADOS
        botones_sizer = wx.BoxSizer(wx.HORIZONTAL)
        botones_sizer.Add(self.boton, 0, wx.ALL, 5)
        botones_sizer.Add(self.botonCerrar, 0, wx.ALL, 5)
        sizer.Add(botones_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(sizer)

    # Funciones de botones al clickear
    def on_boton_click(self, event):
        usuario = self.usuario.GetValue()
        contraseña = self.contraseña.GetValue()
        if usuario == 'administrador' and contraseña == 'Unitutor':
            wx.MessageBox('Inicio de sesion exitoso', 'Exito', wx.OK | wx.ICON_INFORMATION)
            self.GetParent().VentanaMenuPrincipal()
        else:
            wx.MessageBox('Usuario o contraseña incorrectos', 'Error', wx.OK | wx.ICON_ERROR)

    def on_boton_cerrar(self, event):
        self.GetParent().Close()
    
    def color_fondo(self): #Celeste claro
        color = wx.Colour("#E8F0FE")
        self.SetBackgroundColour(color)
        self.Refresh()


#---------------------------------------------------------------------------
class MiVentana(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Unitutor')
        panel = MiPanel(self)
        self.Show()
    
    #abrir modtutores.py
    def VentanaMenuPrincipal(self):
        self.Hide() #Oculta ventana actual
        # Abrir la ventana principal del módulo de tutores
        menu_principal = modtutores.UNITORAppFrame()
        menu_principal.Centre()
        menu_principal.Show()
#---------------------------------------------------------------------------
#resolucion de pantalla
if __name__ == '__main__':
    app = wx.App(redirect=False)

    pn = os.path.normpath(os.path.join(bitmapDir, "Unitutor.png"))
    if not os.path.exists(pn):
        pn = os.path.normpath(os.path.join(os.path.dirname(__file__), 'Logo', 'LogoSplash.png'))
    bitmap = wx.Bitmap(pn, wx.BITMAP_TYPE_PNG)

    splash = AS.AdvancedSplash(None, bitmap=bitmap, timeout=1500, agwStyle=AS.AS_TIMEOUT | AS.AS_CENTER_ON_PARENT)
    splash.Show()

    def al_cerrar_splash(evt):
        splash.Hide()
        frame = MiVentana()
        frame.SetSize(600, 400)
        frame.Centre()
        frame.Show()
        evt.Skip()

    splash.Bind(wx.EVT_CLOSE, al_cerrar_splash)
    app.MainLoop()