import flet as ft
from database import AyurvedaDB
import datetime

def main(page: ft.Page):
    # --- Configuración General ---
    page.title = "Ayurveda & Coaching"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.TEAL,
        font_family="Roboto" # Usamos una fuente standard limpia
    )
    # Fondo cálido y premium
    page.bgcolor = ft.Colors.ORANGE_50
    page.padding = 0 
    
    # Inicializar Base de Datos (V5)
    db = AyurvedaDB("pacientes_v5.db")
    
    # --- Helpers ---
    def calculate_age_str(birth_date_str):
        if not birth_date_str: return "N/A"
        try:
            birth_date = datetime.datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            today = datetime.date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return str(age)
        except:
            return "?"

    def create_compact_slider(label, color, initial_value=5):
        """Crea un control de columna con Label y Slider."""
        # Slider más compacto (height=20)
        slider = ft.Slider(min=0, max=10, divisions=10, value=initial_value, label="{value}", active_color=color, height=20)
        return ft.Column([
            ft.Text(label, size=11, color=color, weight="bold"),
            slider
        ], spacing=0, expand=True)

    # --- Route Handler ---
    def route_change(route):
        page.views.clear()
        
        troute = ft.TemplateRoute(page.route)
        
        # ---------------------------------------------------------
        # 1. HOME (Landing)
        # ---------------------------------------------------------
        if troute.match("/"):
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.AppBar(
                            title=ft.Text("Ayurveda Manager"), 
                            center_title=True,
                            bgcolor=ft.Colors.TEAL_700, 
                            color=ft.Colors.WHITE,
                            elevation=4
                        ),
                        ft.Container(
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.top_center,
                                end=ft.alignment.bottom_center,
                                colors=[ft.Colors.ORANGE_50, ft.Colors.ORANGE_100],
                            ),
                            padding=20,
                            alignment=ft.alignment.center,
                            content=ft.Column([
                                ft.Icon(ft.Icons.SPA, size=100, color=ft.Colors.TEAL_600),
                                ft.Text("Gestión de Pacientes", size=24, weight="bold", color=ft.Colors.BROWN_800),
                                ft.Text("Ayurveda y Coaching", size=16, color=ft.Colors.BROWN_600),
                                ft.Container(height=40),
                                ft.ElevatedButton(
                                    content=ft.Container(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.PEOPLE, size=30, color=ft.Colors.WHITE),
                                            ft.Text("VER PACIENTES", size=18, weight="bold", color=ft.Colors.WHITE),
                                        ], alignment=ft.MainAxisAlignment.CENTER),
                                        padding=ft.padding.symmetric(vertical=15, horizontal=20)
                                    ),
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.Colors.TEAL_600,
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                        elevation=5
                                    ),
                                    on_click=lambda _: page.go("/pacientes")
                                )
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                            expand=True
                        )
                    ],
                    padding=0,
                    scroll=ft.ScrollMode.AUTO
                )
            )

        # ---------------------------------------------------------
        # 2. LISTA DE PACIENTES
        # ---------------------------------------------------------
        elif troute.match("/pacientes"):
            pacientes_list = db.get_patients()
            
            list_items = []
            if not pacientes_list:
                list_items.append(
                    ft.Container(
                        content=ft.Text("No hay pacientes registrados.", italic=True, color=ft.Colors.GREY_700),
                        alignment=ft.alignment.center,
                        padding=40
                    )
                )
            
            for p in pacientes_list:
                age_str = calculate_age_str(p['fecha_nacimiento'])
                list_items.append(
                    ft.Card(
                        content=ft.ListTile(
                            leading=ft.CircleAvatar(
                                content=ft.Text(p['nombre'][0].upper(), weight="bold"), 
                                bgcolor=ft.Colors.TEAL_100, 
                                color=ft.Colors.TEAL_900
                            ),
                            title=ft.Text(p['nombre'], weight="bold", size=16),
                            subtitle=ft.Text(f"Edad: {age_str} | Tel: {p['telefono'] or '-'}", size=12),
                            trailing=ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.TEAL_600, on_click=lambda e, pid=p['id']: page.go(f"/editar_paciente/{pid}")),
                            on_click=lambda e, pid=p['id']: page.go(f"/paciente/{pid}")
                        ),
                        elevation=2,
                        color=ft.Colors.WHITE,
                        margin=ft.margin.only(bottom=8)
                    )
                )

            page.views.append(
                ft.View(
                    "/pacientes",
                    [
                        ft.AppBar(title=ft.Text("Pacientes"), bgcolor=ft.Colors.TEAL_700, color=ft.Colors.WHITE),
                        ft.Container(
                            padding=15,
                            content=ft.Column([
                                ft.ListView(controls=list_items, expand=True, spacing=5),
                                ft.Container(height=10),
                                ft.FloatingActionButton(
                                    icon=ft.Icons.ADD,
                                    bgcolor=ft.Colors.DEEP_ORANGE_500,
                                    on_click=lambda _: page.go("/nuevo_paciente")
                                )
                            ], expand=True),
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.top_center, 
                                end=ft.alignment.bottom_center, 
                                colors=[ft.Colors.ORANGE_50, ft.Colors.WHITE]
                            )
                        )
                    ],
                    padding=0
                )
            )

        # ---------------------------------------------------------
        # 3. FORMULARIO PACIENTE (NUEVO / EDITAR)
        # ---------------------------------------------------------
        elif troute.match("/nuevo_paciente") or troute.match("/editar_paciente/:id"):
            is_edit = "/editar_paciente/" in page.route
            patient_id = troute.id if is_edit else None
            
            # Datos iniciales
            p_data = {}
            if is_edit:
                p_data = db.get_patient(patient_id)
                if not p_data:
                    page.go("/pacientes")
                    return

            # Inputs
            txt_nombre = ft.TextField(label="Nombre Completo", text_size=14, border_color=ft.Colors.TEAL, value=p_data.get("nombre", ""))
            txt_domicilio = ft.TextField(label="Domicilio", text_size=14, border_color=ft.Colors.TEAL, value=p_data.get("domicilio", ""))
            txt_telefono = ft.TextField(label="Teléfono", keyboard_type=ft.KeyboardType.PHONE, text_size=14, border_color=ft.Colors.TEAL, value=p_data.get("telefono", ""))
            
            # Fecha y Edad calculada
            def on_dob_change(e):
                age_lbl.value = f"Edad: {calculate_age_str(txt_nacimiento.value)}"
                age_lbl.update()

            txt_nacimiento = ft.TextField(
                label="Fecha Nac. (YYYY-MM-DD)", 
                hint_text="Ej: 1990-12-31", 
                text_size=14, 
                border_color=ft.Colors.TEAL,
                value=p_data.get("fecha_nacimiento", ""),
                on_change=on_dob_change
            )
            initial_age = calculate_age_str(p_data.get("fecha_nacimiento", ""))
            age_lbl = ft.Text(f"Edad: {initial_age}", size=14, weight="bold", color=ft.Colors.TEAL_800)

            txt_nota = ft.TextField(label="Antecedentes / Notas", multiline=True, min_lines=3, border_color=ft.Colors.TEAL, value=p_data.get("nota", ""))

            # Sliders (extraer helper)
            v_vata = create_compact_slider("Vata (Aire)", ft.Colors.BLUE, p_data.get("prakruti_vata", 5))
            v_pitta = create_compact_slider("Pitta (Fuego)", ft.Colors.RED, p_data.get("prakruti_pitta", 5))
            v_kapha = create_compact_slider("Kapha (Tierra)", ft.Colors.GREEN, p_data.get("prakruti_kapha", 5))
            
            g_sattva = create_compact_slider("Sattva", ft.Colors.AMBER, p_data.get("prakruti_sattva", 5))
            g_rajas = create_compact_slider("Rajas", ft.Colors.ORANGE, p_data.get("prakruti_rajas", 5))
            g_tamas = create_compact_slider("Tamas", ft.Colors.GREY, p_data.get("prakruti_tamas", 5))

            def guardar_paciente(e):
                if not txt_nombre.value:
                    txt_nombre.error_text = "El nombre es obligatorio"
                    txt_nombre.update()
                    return
                
                data = {
                    "id": patient_id, # None si es nuevo
                    "nombre": txt_nombre.value,
                    "domicilio": txt_domicilio.value,
                    "telefono": txt_telefono.value,
                    "fecha_nacimiento": txt_nacimiento.value,
                    "nota": txt_nota.value,
                    "prakruti_vata": v_vata.controls[1].value,
                    "prakruti_pitta": v_pitta.controls[1].value,
                    "prakruti_kapha": v_kapha.controls[1].value,
                    "prakruti_sattva": g_sattva.controls[1].value,
                    "prakruti_rajas": g_rajas.controls[1].value,
                    "prakruti_tamas": g_tamas.controls[1].value,
                }
                db.save_patient(data)
                page.snack_bar = ft.SnackBar(ft.Text("Paciente guardado correctamente"))
                page.snack_bar.open = True
                page.go("/pacientes")

            title_text = "Editar Ficha" if is_edit else "Nueva Ficha"
            
            page.views.append(
                ft.View(
                    page.route,
                    [
                        ft.AppBar(title=ft.Text(title_text), bgcolor=ft.Colors.TEAL_700, color=ft.Colors.WHITE),
                        ft.Container(
                            padding=20,
                            content=ft.Column([
                                ft.Text("Datos Personales", size=16, weight="bold", color=ft.Colors.TEAL_900),
                                txt_nombre,
                                txt_domicilio,
                                ft.Row([ft.Column([txt_nacimiento], expand=True), ft.Column([age_lbl], expand=False)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                txt_telefono,
                                ft.Divider(),
                                ft.Text("Constitución Prakruti (Doshas)", size=16, weight="bold", color=ft.Colors.TEAL_900),
                                ft.Row([v_vata, v_pitta, v_kapha], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                                ft.Divider(),
                                ft.Text("Estado Mental (Gunas)", size=16, weight="bold", color=ft.Colors.TEAL_900),
                                ft.Row([g_sattva, g_rajas, g_tamas], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                                ft.Divider(),
                                txt_nota,
                                ft.Container(height=20),
                                ft.ElevatedButton(
                                    "Guardar Ficha", 
                                    icon=ft.Icons.SAVE, 
                                    bgcolor=ft.Colors.TEAL_700, 
                                    color=ft.Colors.WHITE, 
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                    width=float('inf'), 
                                    height=50,
                                    on_click=guardar_paciente
                                )
                            ] )
                        )
                    ],
                    bgcolor=ft.Colors.WHITE,
                    scroll=ft.ScrollMode.AUTO
                )
            )

        # ---------------------------------------------------------
        # 4. VISTA DETALLE PACIENTE (DASHBOARD)
        # ---------------------------------------------------------
        elif troute.match("/paciente/:id"):
            patient_id = troute.id
            patient = db.get_patient(patient_id)
            if not patient:
                page.go("/pacientes")
                return
            
            consultas = db.get_consultations_by_patient(patient_id)
            age = calculate_age_str(patient['fecha_nacimiento'])
            
            # --- Cards de Info ---
            def info_row(icon, label, value):
                return ft.Row([ft.Icon(icon, size=16, color=ft.Colors.TEAL), ft.Text(f"{label}: ", weight="bold"), ft.Text(value)], spacing=5)

            # --- Lista Historial ---
            history_tiles = []
            if consultas:
                for c in consultas:
                    history_tiles.append(
                        ft.Container(
                           bgcolor=ft.Colors.WHITE,
                           border=ft.border.all(1, ft.Colors.GREY_300),
                           border_radius=8,
                           padding=10,
                           content=ft.Column([
                               ft.Row([
                                   ft.Icon(ft.Icons.CALENDAR_MONTH, size=16, color=ft.Colors.TEAL),
                                   ft.Text(f"{c['fecha']}", weight="bold"),
                                   ft.Container(expand=True),
                                   ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=ft.Colors.GREY)
                               ]),
                               ft.Text(f"Motivo: {c['motivo']}", size=13, weight="w500"),
                               ft.Text(f"Síntomas: {c.get('sintomas', '-')}", size=12, italic=True, color=ft.Colors.GREY_700),
                               ft.Text(f"Vikruti: V{int(c.get('vikruti_vata',0))} P{int(c.get('vikruti_pitta',0))} K{int(c.get('vikruti_kapha',0))}", size=11, color=ft.Colors.TEAL),
                               ft.Divider(height=5),
                               ft.Text(f"Tratamiento: {c.get('tratamiento', '')}", size=12, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)
                           ])
                        )
                    )
            else:
                history_tiles.append(ft.Text("No hay consultas registradas.", italic=True))

            page.views.append(
                ft.View(
                    f"/paciente/{patient_id}",
                    [
                        ft.AppBar(
                            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/pacientes"), tooltip="Volver a Lista"),
                            title=ft.Text(patient['nombre']), 
                            bgcolor=ft.Colors.TEAL_700, 
                            color=ft.Colors.WHITE, 
                            actions=[
                                ft.IconButton(ft.Icons.EDIT, tooltip="Editar Ficha", on_click=lambda _: page.go(f"/editar_paciente/{patient_id}"))
                            ]
                        ),
                        ft.Container(
                            padding=15,
                            content=ft.Column([
                                # HEADER INFO
                                ft.Container(
                                    padding=15,
                                    bgcolor=ft.Colors.TEAL_50,
                                    border_radius=10,
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Icon(ft.Icons.PERSON, size=40, color=ft.Colors.TEAL_800),
                                            ft.Column([
                                                ft.Text(patient['nombre'], size=18, weight="bold", color=ft.Colors.TEAL_900),
                                                ft.Text(f"Edad: {age} años", size=12)
                                            ])
                                        ]),
                                        ft.Divider(color=ft.Colors.TEAL_200),
                                        info_row(ft.Icons.PHONE, "Tel", patient.get('telefono', '-')),
                                        info_row(ft.Icons.HOME, "Dom", patient.get('domicilio', '-')),
                                        ft.Container(height=5),
                                        ft.Text("Antecedentes:", weight="bold", size=12),
                                        ft.Text(patient.get('nota', '-'), size=12, italic=True),
                                        ft.Container(height=5),
                                        ft.Container(height=5),
                                        # Doshas y Gunas Explicitos
                                        ft.Row([
                                            ft.Column([
                                                ft.Text("Prakruti (Doshas)", size=12, weight="bold", color=ft.Colors.TEAL_900),
                                                ft.Text(f"Vata: {int(patient['prakruti_vata'])}", size=12),
                                                ft.Text(f"Pitta: {int(patient['prakruti_pitta'])}", size=12),
                                                ft.Text(f"Kapha: {int(patient['prakruti_kapha'])}", size=12),
                                            ]),
                                            ft.VerticalDivider(width=20, color=ft.Colors.GREY_300),
                                            ft.Column([
                                                ft.Text("Gunas (Mente)", size=12, weight="bold", color=ft.Colors.ORANGE_900),
                                                ft.Text(f"Sattva: {int(patient['prakruti_sattva'])}", size=12),
                                                ft.Text(f"Rajas: {int(patient['prakruti_rajas'])}", size=12),
                                                ft.Text(f"Tamas: {int(patient['prakruti_tamas'])}", size=12),
                                            ])
                                        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, vertical_alignment=ft.CrossAxisAlignment.START)
                                    ])
                                ),
                                ft.Container(height=15),
                                
                                # SECCION CONSULTAS
                                ft.Row([
                                    ft.Text("Historial de Consultas", size=16, weight="bold", color=ft.Colors.TEAL_900),
                                    ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color=ft.Colors.DEEP_ORANGE, tooltip="Nueva Consulta", on_click=lambda _: page.go(f"/consulta/{patient_id}"))
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                
                                # LISTA SCROLLEABLE
                                ft.Column(history_tiles, spacing=10, scroll=ft.ScrollMode.AUTO, expand=False), # Expand false para q use el scroll del view o del container
                                ft.Container(height=20),
                                ft.OutlinedButton("Volver a Lista de Pacientes", icon=ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/pacientes"), width=float('inf'))
                            ] )
                        )
                    ],
                    bgcolor=ft.Colors.WHITE,
                    scroll=ft.ScrollMode.AUTO
                )
            )

        # ---------------------------------------------------------
        # 5. NUEVA CONSULTA
        # ---------------------------------------------------------
        elif troute.match("/consulta/:paciente_id"):
             patient_id = troute.paciente_id
             
             # Inputs
             txt_fecha = ft.TextField(label="Fecha", value=datetime.date.today().strftime("%Y-%m-%d"), border_color=ft.Colors.TEAL)
             txt_motivo = ft.TextField(label="Motivo de Consulta", border_color=ft.Colors.TEAL)
             txt_sintomas = ft.TextField(label="Síntomas", multiline=True, min_lines=2, border_color=ft.Colors.TEAL)
             
             # Sliders Vikruti (Estado Actual)
             k_vik_v = create_compact_slider("Vata (Vikruti)", ft.Colors.BLUE, 0)
             k_vik_p = create_compact_slider("Pitta (Vikruti)", ft.Colors.RED, 0)
             k_vik_k = create_compact_slider("Kapha (Vikruti)", ft.Colors.GREEN, 0)

             # Sliders Gunas (Estado Mental)
             k_gun_s = create_compact_slider("Sattva (Equilibrio)", ft.Colors.AMBER, 5)
             k_gun_r = create_compact_slider("Rajas (Pasión)", ft.Colors.ORANGE, 5)
             k_gun_t = create_compact_slider("Tamas (Inercia)", ft.Colors.GREY, 5)

             txt_tratamiento = ft.TextField(label="Tratamiento / Sugerencias", multiline=True, min_lines=4, border_color=ft.Colors.TEAL)
             txt_detalle = ft.TextField(label="Detalles Privados / Notas extra", multiline=True, min_lines=2, border_color=ft.Colors.TEAL)
             
             def guardar_cons(e):
                 if not txt_motivo.value:
                     txt_motivo.error_text = "Requerido"
                     txt_motivo.update()
                     return

                 data = {
                    "paciente_id": patient_id,
                    "fecha": txt_fecha.value,
                    "motivo": txt_motivo.value,
                    "sintomas": txt_sintomas.value,
                    "vikruti_vata": k_vik_v.controls[1].value,
                    "vikruti_pitta": k_vik_p.controls[1].value,
                    "vikruti_kapha": k_vik_k.controls[1].value,
                    "guna_sattva": k_gun_s.controls[1].value,
                    "guna_rajas": k_gun_r.controls[1].value,
                    "guna_tamas": k_gun_t.controls[1].value,
                    "tratamiento": txt_tratamiento.value,
                    "detalle": txt_detalle.value
                }
                 db.save_consultation(data)
                 page.go(f"/paciente/{patient_id}")

             page.views.append(
                ft.View(
                    f"/consulta/{patient_id}",
                    [
                        ft.AppBar(title=ft.Text("Registrar Consulta"), bgcolor=ft.Colors.TEAL_700, color=ft.Colors.WHITE),
                        ft.Container(
                            padding=20,
                            content=ft.Column([
                                txt_fecha,
                                txt_motivo,
                                txt_sintomas,
                                ft.Divider(),
                                ft.Text("Vikruti (Desequilibrio Actual)", weight="bold"),
                                ft.Row([k_vik_v, k_vik_p, k_vik_k], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                                ft.Divider(),
                                ft.Text("Estado Mental (Gunas)", weight="bold"),
                                ft.Row([k_gun_s, k_gun_r, k_gun_t], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                                ft.Divider(),
                                txt_tratamiento,
                                txt_detalle,
                                ft.Container(height=20),
                                ft.ElevatedButton("Guardar Consulta", icon=ft.Icons.SAVE, bgcolor=ft.Colors.TEAL_700, color=ft.Colors.WHITE, width=float('inf'), height=50, on_click=guardar_cons)
                            ] )
                        )
                    ],
                    bgcolor=ft.Colors.WHITE,
                    scroll=ft.ScrollMode.AUTO
                )
             )

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")

ft.app(target=main)
