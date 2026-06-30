#!/usr/bin/env python
from Backend import modreportes
from Backend import modtutores
from Backend import modtutorias
import Backend as backend
import wx.lib.agw.aquabutton as AB
import os
import pprint
import wx
import wx.adv
import wx.dataview as dv
from wx.lib.wordwrap import wordwrap

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(os.path.dirname(DATA_DIR), "Datos")
if not os.path.isdir(DATA_ROOT):
    DATA_ROOT = DATA_DIR
ESTUDIANTES_FILE = os.path.join(DATA_ROOT, "datos_estudiantes.py")

# ----------------------------------------------------------------------
# MODELO DE DATOS INTERACTIVO (DataViewIndexListModel)
# ----------------------------------------------------------------------
class EstudiantesModel(dv.DataViewIndexListModel):
    def __init__(self, data):
        # datos iniciales
        super().__init__(len(data))
        # Validar cambios al editar una celda
        self.all_data = list(data)
        #muestra los estudiantes en la tabla
        self.data = list(data)

    def GetColumnType(self, col):
        return "string"

    def GetValueByRow(self, row, col): # Obtiene el valor de una celda específica.
        return self.data[row][col]

    def SetValueByRow(self, value, row, col):
        # Se ejecuta de forma automática cuando el usuario edita una celda
        if col == 4:
            estados_validos = {"Activo", "Inactivo"}
            if value not in estados_validos:
                wx.MessageBox(
                    f"Valor de estado '{value}' no se reconoce. Usa 'Activo' o 'Inactivo'.",
                    "Valor de Estado Incorrecto",
                    wx.OK | wx.ICON_WARNING,
                )
                return False
        self.data[row][col] = value #actualiza el valor de la tabla
        
        # Busca el estudiante por su legajo
        legajo_modificado = self.data[row][0]   #obtiene el legajo del estudainte
        for registro in self.all_data: #recorre la funcion
            if registro[0] == legajo_modificado: #comprueba si coincide con el legajo modificado
                registro[col] = value #actualiza el dato
                break    
                
        # Actualizar la tabla
        self.RowChanged(row)
        return True

    def GetColumnCount(self): #cantidad de columnas
        return 5

    def GetCount(self): #cantidad de filas
        return len(self.data)

    def GetAttrByRow(self, row, col, attr):
        # Cambia el color según el estado
        if col == 4:
            estado = self.data[row][col]
            if estado == "Activo":
                attr.SetColour(wx.Colour(34, 139, 34))  # Verde bosque    si cambia a "activo" este cambia a verde
                attr.SetBold(True)
            elif estado == "Inactivo":
                attr.SetColour(wx.Colour(178, 34, 34))  # Rojo fuego      si cambia a "inactivo" este cambia a rojo
                attr.SetBold(True)
            
            return True
        return False

    def Compare(self, item1, item2, col, ascending):
        if not ascending:
            item2, item1 = item1, item2
        row1 = self.GetRow(item1)
        row2 = self.GetRow(item2)
        a = self.data[row1][col]
        b = self.data[row2][col]
        
        # Compara el número del legajo con el siguiente/anterior
        if col in [0, 3]:
            try:
                a_num = int(''.join(filter(str.isdigit, a))) 
                b_num = int(''.join(filter(str.isdigit, b)))
                if a_num < b_num: return -1 
                if a_num > b_num: return 1
                return 0
            except ValueError:
                pass
                
        if a < b: return -1
        if a > b: return 1
        return 0

    def AddRow(self, value): #para agregar una nueva fila
        self.data.append(value)  #el dato que se muestra en la tabla
        self.all_data.append(value)
        self.RowAppended() #agrega una nueva fila

    def DeleteRows(self, rows):
        # Elimina en orden inverso para evitar desfase de índices
        rows = sorted(rows, reverse=True)
        for row in rows:
            legajo_a_borrar = self.data[row][0]
            del self.data[row]
            self.RowDeleted(row)
            #borra al estudiante de la lista
            self.all_data = [r for r in self.all_data if r[0] != legajo_a_borrar]

    def FilterData(self, text):
        """Filtra la lista en tiempo real por Nombre o Legajo sin perder la lista maestra."""
        text = text.lower().strip()
        if not text:
            self.data = list(self.all_data)
        else:
            self.data = [
                r for r in self.all_data 
                if text in r[0].lower() or text in r[1].lower()
            ]
        # Actualiza la tabla con los resultados del filtro
        self.Reset(len(self.data))


# ----------------------------------------------------------------------
# PANEL DEL MÓDULO: GESTIÓN DE ESTUDIANTES (SCREEN 3 - B)
# ----------------------------------------------------------------------
class EstudiantesPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        datos_iniciales = self.cargarestudiantesdatos()

        self.model = EstudiantesModel(datos_iniciales)

        # Sizer Principal del panel
        sizer_efectos = wx.BoxSizer(wx.VERTICAL)

        # 1. Título de la sección
        lbl_titulo = wx.StaticText(self, label="Gestión de Estudiantes")
        lbl_titulo.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer_efectos.Add(lbl_titulo, 0, wx.ALL, 10)

        # 2. Barra de Búsqueda (Filtro interactivo)
        sizer_busqueda = wx.BoxSizer(wx.HORIZONTAL)
        lbl_buscar = wx.StaticText(self, label="Buscar")
        sizer_busqueda.Add(lbl_buscar, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        self.txt_buscar = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.txt_buscar.SetHint("Nombre o Legajo")
        sizer_busqueda.Add(self.txt_buscar, 1, wx.EXPAND | wx.RIGHT, 5)

        self.btn_buscar = wx.Button(self, label="Buscar")
        self.btn_limpiar = wx.Button(self, label="Limpiar")
        sizer_busqueda.Add(self.btn_buscar, 0, wx.RIGHT, 5)
        sizer_busqueda.Add(self.btn_limpiar, 0)
        
        sizer_efectos.Add(sizer_busqueda, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # 3. Control de Vista de Datos Avanzado (DataViewCtrl)
        self.dvc = dv.DataViewCtrl(self, style=wx.BORDER_THEME | dv.DV_ROW_LINES | dv.DV_VERT_RULES | dv.DV_MULTIPLE)
        self.dvc.AssociateModel(self.model)

        # Inserción de columnas requeridas mapeadas al modelo indexado
        self.dvc.AppendTextColumn("Legajo", 0, width=65, mode=dv.DATAVIEW_CELL_INERT)
        self.dvc.AppendTextColumn("Nombre y Apellido", 1, width=170, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvc.AppendTextColumn("Carrera", 2, width=150, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvc.AppendTextColumn("Año", 3, width=65, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvc.AppendTextColumn("Estado", 4, width=95, mode=dv.DATAVIEW_CELL_EDITABLE)

        # Permitir ordenar/reordenar por columnas
        for col in self.dvc.Columns:
            col.Sortable = True
            col.Reorderable = True

        sizer_efectos.Add(self.dvc, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10) #expande y agrega espacio a los costados

        # 4. Panel Inferior (Botones de acción + Contador Dinámico)
        sizer_acciones = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_agregar = wx.Button(self, label="+ Agregar")
        self.btn_eliminar = wx.Button(self, label="Eliminar")
        
        sizer_acciones.Add(self.btn_agregar, 0, wx.RIGHT, 5)
        sizer_acciones.Add(self.btn_eliminar, 0, wx.RIGHT, 10)
        
        # Espaciador elástico para empujar el contador a la derecha de la interfaz
        sizer_acciones.AddStretchSpacer()
        
        # Componente de conteo 
        self.lbl_contador = wx.StaticText(self, label="")
        self.lbl_contador.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer_acciones.Add(self.lbl_contador, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        sizer_efectos.Add(sizer_acciones, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_efectos)

        # Eventos
        self.btn_buscar.Bind(wx.EVT_BUTTON, self.OnFiltrarBusqueda)
        self.btn_limpiar.Bind(wx.EVT_BUTTON, self.OnLimpiarBusqueda)
        self.txt_buscar.Bind(wx.EVT_TEXT_ENTER, self.OnFiltrarBusqueda)
        
        self.btn_agregar.Bind(wx.EVT_BUTTON, self.OnAgregarRegistro)
        self.btn_eliminar.Bind(wx.EVT_BUTTON, self.OnEliminarRegistros)
        
        self.Bind(dv.EVT_DATAVIEW_ITEM_VALUE_CHANGED, self.OnCeldaEditada, self.dvc)

        # Mostrar el contador al iniciar
        self.ActualizarContador()

    #cambiar a la ventana tutores al apretar el boton "tutores" de la parte superior
    def CambiarVentanaTutores(self):
        self.GetParent().VentanaMenuPrincipal()
    
    
        
    


    def ActualizarContador(self):
        """Calcula de la lista maestra en memoria cuántos registros están activos."""
        activos = len([reg for reg in self.model.all_data if reg[4].strip().lower() == "activo"])
        total = len(self.model.all_data)
        self.lbl_contador.SetLabel(f"Resultados Activos: {activos} (Total: {total})")
        self.Layout()

    def cargarestudiantesdatos(self):
        """Carga los datos de estudiantes desde un archivo Python local."""
        if os.path.exists(ESTUDIANTES_FILE):
            try:
                namespace = {}
                with open(ESTUDIANTES_FILE, "r", encoding="utf-8") as f:
                    code = f.read()
                exec(code, namespace)
                data = namespace.get("ESTUDIANTES")
                if isinstance(data, list) and all(isinstance(row, list) for row in data):
                    return data
            except OSError:
                pass

        datos_iniciales = [
            ["T-001", "Pérez, Lucas", "Software", "1°", "Activo"],
            ["T-002", "Gómez, Laura", "Autom & Control", "2°", "Activo"],
            ["T-003", "Rodríguez, Sofía", "Biotecnología", "1°", "Inactivo"]
        ]
        self.GuardarEstudiantetData(datos_iniciales)
        return datos_iniciales

    def GuardarEstudiantetData(self, data=None):
        """Guarda los datos de estudiantes en un archivo Python local."""
        data_to_save = self.model.all_data if data is None else data
        try:
            with open(ESTUDIANTES_FILE, "w", encoding="utf-8") as f:
                f.write("# Archivo de datos generado automáticamente\n")
                f.write("ESTUDIANTES = ")
                f.write(pprint.pformat(data_to_save, width=120))
                f.write("\n")
        except OSError:
            wx.LogError("No se pudo guardar el archivo de datos de estudiantes.")

    def OnFiltrarBusqueda(self, evt):
        self.model.FilterData(self.txt_buscar.GetValue())

    def OnLimpiarBusqueda(self, evt):
        self.txt_buscar.SetValue("")
        self.model.FilterData("")

    def OnAgregarRegistro(self, evt):
        # Generar el siguiente legajo
        ids_existentes = []
        for r in self.model.all_data:
            try:
                num = int(''.join(filter(str.isdigit, r[0])))
                ids_existentes.append(num)
            except ValueError:
                pass
        siguiente_id = max(ids_existentes) + 1 if ids_existentes else 1
        nuevo_legajo = f"T-{siguiente_id:03d}"

        # Insertamos una nueva fila editable por defecto
        nuevo_estudiante = [nuevo_legajo, "Nuevo Alumno", "Asignar Carrera", "1°", "Activo"]
        self.model.AddRow(nuevo_estudiante)
        self.GuardarEstudiantetData()
        self.ActualizarContador()

    def OnModificarRegistro(self, evt):
        item = self.dvc.GetSelection()
        if not item.IsOk():
            wx.MessageBox("Por favor, haz doble clic directamente sobre cualquier celda de la tabla para editar sus datos.", 
                          "Modo de Edición Directa", wx.OK | wx.ICON_INFORMATION)

    def OnEliminarRegistros(self, evt):
        items = self.dvc.GetSelections()
        if not items:
            wx.MessageBox("Selecciona una o más filas de la lista para proceder a eliminarlas.", 
                          "Atención", wx.OK | wx.ICON_WARNING)
            return
            
        rows = [self.model.GetRow(item) for item in items]
        self.model.DeleteRows(rows)
        self.GuardarEstudiantetData()
        self.ActualizarContador()

    def OnCeldaEditada(self, evt):
        # Cada vez que el modelo confirma un cambio, recalcula los resultados activos
        self.GuardarEstudiantetData()
        self.ActualizarContador()


# ----------------------------------------------------------------------
# VENTANA PRINCIPAL DE LA APLICACIÓN (Navegación Superior Modificada)
# ----------------------------------------------------------------------
class UNITORAppFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="UNITUTOR - Gestión de Tutorías", size=(780, 520))

        #Logo pequeño para el borde de ventana al lado de titulo
        logo_pequeño = wx.Image('Logo/Unitutor.png', wx.BITMAP_TYPE_PNG)
        logo_pequeño = logo_pequeño.Scale(32, 32, wx.IMAGE_QUALITY_HIGH)
        logo_pequeño_bmp = wx.Bitmap(logo_pequeño)
        self.GetTopLevelParent().SetIcon(wx.Icon(logo_pequeño_bmp))

        # Contenedor de distribución vertical completo
        sizer_ventana = wx.BoxSizer(wx.VERTICAL)

        # PANEL SUPERIOR DE NAVEGACIÓN (Sustituye completamente al panel izquierdo antiguo)
        self.panel_navegacion = wx.Panel(self)
        # Barra de navegación
        sizer_nav = wx.BoxSizer(wx.HORIZONTAL)

        lbl_modulos = wx.StaticText(self.panel_navegacion)
        lbl_modulos.SetForegroundColour(wx.Colour(200, 200, 200))
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

        # Opciones
        modulos_superiores = ["Tutores", "Estudiantes", "Tutorías", "Reportes"]
        
        for mod in modulos_superiores:
            # Panel contenedor: usar el mismo fondo que la barra de navegación
            btn_panel = wx.Panel(self.panel_navegacion)
            nav_bg = self.panel_navegacion.GetBackgroundColour()
            fg = wx.Colour(50, 50, 50)
            if mod == "Estudiantes":   #si estamos en el modulo de "Estudiantes" el boton esta oscuro
                fg = wx.Colour(255, 255, 255)

            btn_panel.SetBackgroundColour(nav_bg)
            btn = AB.AquaButton(btn_panel, -1, label=mod)
            btn.SetForegroundColour(fg)
            btn.SetHoverColour(wx.Colour(155, 200, 230) if mod == "Estudiantes" else wx.Colour(220, 220, 220))
            btn.SetFocusColour(wx.Colour(30, 90, 140) if mod == "Estudiantes" else wx.Colour(180, 180, 180))

            # Botones
            if mod == "Tutores":
                btn.Bind(wx.EVT_BUTTON, self.VentanaMenuPrincipal)
            elif mod == "Tutorías":
                btn.Bind(wx.EVT_BUTTON, self.AbrirTutorias)
            elif mod == "Reportes":
                btn.Bind(wx.EVT_BUTTON, self.AbrirReportes)

            sp = wx.BoxSizer(wx.VERTICAL)
            sp.Add(btn, 0, wx.EXPAND, 0) #mete un boton dentro del panel
            btn_panel.SetSizer(sp)
            # Ajustar el tamaño del panel al del botón para evitar un gran fondo cuadrado
            btn_panel.SetMinSize(btn.GetBestSize())

            sizer_nav.Add(btn_panel, 0, wx.ALIGN_CENTER_VERTICAL, 4)

        self.panel_navegacion.SetSizer(sizer_nav)
        sizer_ventana.Add(self.panel_navegacion, 0, wx.EXPAND)

        # Panel principal de estudiantes
        self.panel_contenido = EstudiantesPanel(self)
        sizer_ventana.Add(self.panel_contenido, 1, wx.EXPAND)

        # Barra de estado
        self.CreateStatusBar()
        self.SetStatusText("Módulo Activo: Gestión de Estudiantes | Datos preparados para futura extracción")

        self.SetSizer(sizer_ventana)
        self.Centre()  


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

    def VentanaMenuPrincipal(self, evt=None):
        self.Hide() # Oculta ventana actual
        # Abrir la ventana menu principal del modulo de tutores
        menu_principal = modtutores.UNITORAppFrame()
        menu_principal.Centre()
        menu_principal.Show()
    
    def AbrirTutorias(self, evt=None):
        self.Hide()
        ventana_tutorias = modtutorias.TutoriasAppFrame()
        ventana_tutorias.Centre()
        ventana_tutorias.Show()

    def AbrirReportes(self, evt=None):
        self.Hide()
        ventana_reportes = modreportes.ReportesFrame()
        ventana_reportes.Centre()
        ventana_reportes.Show()
    


if __name__ == "__main__":
    app = wx.App()
    ventana = UNITORAppFrame()
    ventana.Show()
    app.MainLoop()