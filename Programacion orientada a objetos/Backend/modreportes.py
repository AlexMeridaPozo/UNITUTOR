#Ventana parecida en diseño a la de tutores y estudiantes
#Mostrara una estadistica de los tutores registrados, estudiantes inscriptos y tutorias completadas este mes
#los valores se usaran en base a los datos de los archivos de tutores y estudiantes, y se mostraran en la ventana

import os
import sys
import wx
import wx.adv
import wx.lib.agw.aquabutton as AB
from reportlab.pdfgen import canvas
from wx.lib.wordwrap import wordwrap
from reportlab.lib.pagesizes import letter
import Backend as backend
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from Backend import modtutores
from Backend import modestudiantes
from Backend import modtutorias

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(os.path.dirname(DATA_DIR), "Datos")
if not os.path.isdir(DATA_ROOT):
    DATA_ROOT = DATA_DIR
TUTORIAS_FILE = os.path.join(DATA_ROOT, "datos_tutorias.py")
TUTORES_FILE = os.path.join(DATA_ROOT, "datos_tutores.py")
ESTUDIANTES_FILE = os.path.join(DATA_ROOT, "datos_estudiantes.py")


def Carga_Datos_Variable(path, variable_name):
    if not os.path.exists(path):
        return []
    namespace = {}
    with open(path, "r", encoding="utf-8") as f:
        exec(f.read(), namespace)
    data = namespace.get(variable_name)
    if isinstance(data, list):
        return data
    return []


def Cargar_Estudiantes():
    return Carga_Datos_Variable(ESTUDIANTES_FILE, "ESTUDIANTES")


def Cargar_Tutores():
    return Carga_Datos_Variable(TUTORES_FILE, "TUTORES")


def Cargar_Tutorias():
    return Carga_Datos_Variable(TUTORIAS_FILE, "TUTORIAS")


class MiPanelReportes(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.color_fondo()

        # Carga datos desde los archivos en "Datos"
        tutores = Cargar_Tutores()
        estudiantes = Cargar_Estudiantes()
        tutorias = Cargar_Tutorias()

        def Datos():
            tutores_local = Cargar_Tutores()
            estudiantes_local = Cargar_Estudiantes()
            tutorias_local = Cargar_Tutorias()
            num_tutores_loc = sum(1 for t in tutores_local if len(t) > 4 and str(t[4]).strip().lower() == "activo")
            num_estudiantes_loc = sum(1 for e in estudiantes_local if len(e) > 4 and str(e[4]).strip().lower() == "activo")
            num_tutorias_prog_loc = sum(
                1
                for t in tutorias_local
                if len(t) > 4 and str(t[4]).strip().lower() in ("programada", "pendiente")
            )
            num_tutorias_comp_loc = sum(
                1
                for t in tutorias_local
                if len(t) > 4 and str(t[4]).strip().lower() in ("realizada", "completada", "completado")
            )
            return num_tutores_loc, num_estudiantes_loc, num_tutorias_prog_loc, num_tutorias_comp_loc

        num_tutores, num_estudiantes, num_tutorias_programadas, num_tutorias_completadas = Datos()

        sizer = wx.BoxSizer(wx.VERTICAL)

        titulo = wx.StaticText(self, label="Reporte General")
        titulo.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(titulo, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 20)

        panel_grid = wx.GridSizer(2, 2, 10, 10)

        # Cada entrada es: (título, valor, color de fondo)
        tarjetas = [
            ("Tutores", num_tutores, "#AED6F1"),
            ("Estudiantes", num_estudiantes, "#A9DFBF"),
            ("Tutorías programadas", num_tutorias_programadas, "#F9E79F"),
            ("Tutorías completadas", num_tutorias_completadas, "#F5B7B1"),
        ]

        # Guardamos referencias a los labels de valor para actualizar en caliente
        self._valor_labels = {}

        for titulo_tarjeta, valor, color in tarjetas:
            tarjeta = wx.Panel(self, style=wx.BORDER_SIMPLE)
            tarjeta.SetBackgroundColour(wx.Colour(color))
            tarjeta.SetMinSize((180, 120))
            tarjeta_sizer = wx.BoxSizer(wx.VERTICAL)

            etiqueta = wx.StaticText(tarjeta, label=titulo_tarjeta)
            etiqueta.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            tarjeta_sizer.Add(etiqueta, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 15)

            valor_lbl = wx.StaticText(tarjeta, label=str(valor))
            valor_lbl.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            tarjeta_sizer.Add(valor_lbl, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)

            # almacenar referencia
            self._valor_labels[titulo_tarjeta] = valor_lbl

            tarjeta.SetSizer(tarjeta_sizer)
            panel_grid.Add(tarjeta, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(panel_grid, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)

        nota = wx.StaticText(self, label="")
        sizer.Add(nota, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 5)

        self.SetSizer(sizer)

    def color_fondo(self):
        color = wx.Colour("#E8F0FE")
        self.SetBackgroundColour(color)
        self.Refresh()

#para los 4 cuadros del medio, cuenta segun lo que le corresponde
# accede a los datos que le corresponde y accede a la 4ta casilla para ver si coincide con el string
    def actualizar_conteos(self):
        """Relee los archivos de datos y actualiza las etiquetas numéricas en la UI.
        Esto permite que si el módulo de Tutorías guardó cambios en disco, Reportes los refleje al mostrarse."""
        num_tutores = sum(1 for t in Cargar_Tutores() if len(t) > 4 and str(t[4]).strip().lower() == "activo")  
        num_estudiantes = sum(1 for e in Cargar_Estudiantes() if len(e) > 4 and str(e[4]).strip().lower() == "activo") 
        num_tutorias_programadas = sum(1 for t in Cargar_Tutorias() if len(t) > 4 and str(t[4]).strip().lower() in ("programada", "pendiente")) 
        num_tutorias_completadas = sum(1 for t in Cargar_Tutorias() if len(t) > 4 and str(t[4]).strip().lower() in ("realizada", "completada", "completado"))

        mapping = {
            "Tutores": num_tutores,
            "Estudiantes": num_estudiantes,
            "Tutorías programadas": num_tutorias_programadas,
            "Tutorías completadas": num_tutorias_completadas,
        }

        for key, val in mapping.items():
            lbl = self._valor_labels.get(key)
            if lbl:
                lbl.SetLabel(str(val))
        self.Layout()
        


class ReportesFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='UNITUTOR - Gestion de Reportes', size=(780, 520))

        #Logo pequeño para el borde de ventana al lado de titulo
        logo_pequeño = wx.Image('Logo/Unitutor.png', wx.BITMAP_TYPE_PNG)
        logo_pequeño = logo_pequeño.Scale(32, 32, wx.IMAGE_QUALITY_HIGH)
        logo_pequeño_bmp = wx.Bitmap(logo_pequeño)
        self.GetTopLevelParent().SetIcon(wx.Icon(logo_pequeño_bmp))

        sizer_ventana = wx.BoxSizer(wx.VERTICAL)
        sizer_acciones = wx.BoxSizer(wx.HORIZONTAL)

        self.panel_navegacion = wx.Panel(self)
        sizer_nav = wx.BoxSizer(wx.HORIZONTAL)

        lbl_modulos = wx.StaticText(self.panel_navegacion, label="")
        lbl_modulos.SetForegroundColour(wx.Colour(50, 50, 50))
        fuente_mod = lbl_modulos.GetFont()
        fuente_mod.SetWeight(wx.FONTWEIGHT_BOLD)
        lbl_modulos.SetFont(fuente_mod)
        sizer_nav.Add(lbl_modulos, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 15)

        self.panel_navegacion.SetBackgroundColour(wx.Colour("#E8F0FE"))

        menu_bar = wx.MenuBar()
        archivo_menu = wx.Menu()

        archivo_menu.Append(wx.ID_EXIT, "Salir")
        menu_bar.Append(archivo_menu, "Archivo")

        ayuda_menu = wx.Menu()
        self.ID_ACERCA_DE = wx.NewIdRef()
        ayuda_menu.Append(self.ID_ACERCA_DE, "Acerca de...")
        ayuda_menu.Bind(wx.EVT_MENU, self.OnAcercaDe, id=self.ID_ACERCA_DE)
        menu_bar.Append(ayuda_menu, "Ayuda")
        self.SetMenuBar(menu_bar)

        modulos_superiores = ["Tutores", "Estudiantes", "Tutorías", "Reportes"]
        for mod in modulos_superiores:
            btn_panel = wx.Panel(self.panel_navegacion)
            nav_bg = self.panel_navegacion.GetBackgroundColour()
            # Use a consistent dark foreground for all nav buttons
            fg = wx.Colour(50, 50, 50)
            btn_panel.SetBackgroundColour(nav_bg)
            btn = AB.AquaButton(btn_panel, -1, label=mod)
            btn.SetForegroundColour(fg)
            btn.SetHoverColour(wx.Colour(180, 200, 230) if mod == "Reportes" else wx.Colour(220, 220, 220))
            btn.SetFocusColour(wx.Colour(30, 90, 140) if mod == "Reportes" else wx.Colour(180, 180, 180))

            if mod == "Tutorías":
                btn.Bind(wx.EVT_BUTTON, self.AbrirTutorias)
            if mod == "Tutores":
                btn.Bind(wx.EVT_BUTTON, self.AbrirTutores)
            elif mod == "Estudiantes":
                btn.Bind(wx.EVT_BUTTON, self.AbrirEstudiantes)

            sp = wx.BoxSizer(wx.VERTICAL)
            sp.Add(btn, 0, wx.EXPAND, 0)
            btn_panel.SetSizer(sp)
            btn_panel.SetMinSize(btn.GetBestSize())
            sizer_nav.Add(btn_panel, 0, wx.ALIGN_CENTER_VERTICAL, 4)

        self.panel_navegacion.SetSizer(sizer_nav)
        sizer_ventana.Add(self.panel_navegacion, 0, wx.EXPAND)

        self.panel_contenido = MiPanelReportes(self)
        sizer_ventana.Add(self.panel_contenido, 1, wx.EXPAND)

        #boton para exportar reporte a pdf
        self.btn_agregar = wx.Button(self, label="Exportar a PDF")
        self.btn_agregar.Bind(wx.EVT_BUTTON, self.exportar_PDF)
        sizer_acciones.Add(self.btn_agregar, 0, wx.RIGHT, 5)
        sizer_ventana.Add(sizer_acciones, 0, wx.EXPAND | wx.ALL, 10)

        #Boton para printdialog para imprimir
        self.btn_agregar = wx.Button(self, label ="Imprimir")
        self.btn_agregar.Bind(wx.EVT_BUTTON, self.imprimir)
        sizer_acciones.Add(self.btn_agregar, 0, wx.RIGHT, 5)


        self.CreateStatusBar()
        self.SetStatusText("Módulo Activo: Reportes | Datos basados en estudiantes y tutores")

        self.SetSizer(sizer_ventana)
        self.Centre()
        # Aseguramos que los conteos se actualicen cada vez que se muestre el frame
        self.Bind(wx.EVT_SHOW, self.OnShow)
        # Inicializar con conteos correctos
        self.panel_contenido.actualizar_conteos()
    
    def OnAcercaDe(self, evt):
        info = wx.adv.AboutDialogInfo()
        info.Name = "Unitutor"
        info.Version = "1.0"
        info.Description = wordwrap(
            "Unitutor es una aplicación de escritorio creada para gestionar tutorías académicas de forma simple y organizada. "
            "Permite administrar estudiantes, tutores, materias y consultar la información de manera rápida.",
            350, wx.ClientDC(self)
        )
        info.Developers = ["Alex Merida Pozo", "Candela Canteros", "Franco Ingratta"]
        info.Copyright = "© 2026 - Unitutor"
        wx.adv.AboutBox(info)

    def AbrirTutorias(self, evt):
        self.Hide()
        ventana_tutorias = modtutorias.TutoriasAppFrame()
        ventana_tutorias.Centre()
        ventana_tutorias.Show()

    def imprimir(self, evt):
        data = wx.PrintDialogData()

        data.EnableSelection(True)
        data.EnablePrintToFile(True)
        data.EnablePageNumbers(True)
        data.SetMinPage(1)
        data.SetMaxPage(5)
        # data.SetAllPages(True)

        dlg = wx.PrintDialog(self, data)

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetPrintDialogData()
            self.log.WriteText('GetAllPages: %d\n' % data.GetAllPages())

        dlg.Destroy()

    def AbrirTutores(self, evt):
        self.Hide()
        ventana_tutores = modtutores.UNITORAppFrame()
        ventana_tutores.Centre()
        ventana_tutores.Show()

    def AbrirEstudiantes(self, evt):
        self.Hide()
        ventana_estudiantes = modestudiantes.UNITORAppFrame()
        ventana_estudiantes.Centre()
        ventana_estudiantes.Show()

    def exportar_PDF(self, evt):
        # pregunta dónde guardar el archivo
        with wx.FileDialog(self, "Guardar reporte en PDF",
                           wildcard="PDF files (*.pdf)|*.pdf",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dialog:
            if dialog.ShowModal() != wx.ID_OK:
                return
            path = dialog.GetPath()

        #arma el documento

        documento = SimpleDocTemplate(path, pagesize=letter)
        estilos = getSampleStyleSheet()
        bloques = []

        bloques.append(Paragraph("Reporte UNITUTOR", estilos["Title"]))
        bloques.append(Spacer(1, 20))

        #saca los datos de cada uno
        
        bloques +=  self.tabla_de("Tutores", Cargar_Tutores(),
                                   ["Legajo", "Nombre", "Materia", "Disponibilidad", "Estado"], estilos)
        bloques +=  self.tabla_de("Estudiantes", Cargar_Estudiantes(),
                                   ["Legajo", "Nombre", "Carrera", "Año", "Estado"], estilos)
        bloques +=  self.tabla_de("Tutorias", Cargar_Tutorias(),
                                   ["Legajo", "Nombre", "Estudiante", "Fecha", "Estado"], estilos)
        
        #genera pdf

        documento.build(bloques)
        wx.MessageBox(f"PDF exportado correctamente:\n{path}", "Exportación completada", wx.OK | wx.ICON_INFORMATION) 
        #Mensaje que muestra al exportar


    #la estetica que tendra las grillas
    def tabla_de(self, titulo, filas, encabezados, estilos):
        tabla = Table([encabezados] + filas)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4F72")), #color de fondo
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), #color de texto
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey), #color de las grillas
            ("FONTSIZE", (0, 0), (-1, -1), 8),   #el tamaño de la fuente
        ]))
        return [Paragraph(titulo, estilos["Heading2"]), tabla, Spacer(1, 16)]


    def OnShow(self, evt):
        # Cuando la ventana se muestra, actualizar los conteos desde disco
        if evt.IsShown():
            try:
                self.panel_contenido.actualizar_conteos()  #actualiza los datos del panel 
            except Exception: #si hay error ejecuta pass
                pass
        evt.Skip()  #el skip para que el programa se siga ejecutando de forma normal


if __name__ == "__main__":
    app = wx.App()
    ventana = ReportesFrame()
    ventana.Show()
    app.MainLoop()
