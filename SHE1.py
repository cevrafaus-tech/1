import streamlit as st
import pandas as pd
import random
import datetime
from supabase import create_client, Client

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Aquatic Facilities Scheduler Enterprise", layout="wide")

# ==========================================
# CONEXIÓN A BASE DE DATOS EN LA NUBE (SUPABASE)
# ==========================================
# En producción, lee de st.secrets. En local, puedes reemplazar con tus strings directamente para probar.
SUPABASE_URL = st.secrets.get("supabase", {}).get("url", "https://tu-url-temporal.supabase.co")
SUPABASE_KEY = st.secrets.get("supabase", {}).get("key", "tu-key-temporal")

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = get_supabase_client()

# ==========================================
# CONTROL DE ACCESO (GOOGLE OAUTH SIMULADO)
# ==========================================
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'usuario_email' not in st.session_state:
    st.session_state.usuario_email = None

def login_pantalla():
    st.markdown("<h1 style='text-align: center; color: #1a73e8;'>🏊‍♂️ Aquatic Facilities Guard Scheduler</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #5f6368;'>Cloud Management System via Supabase</h4>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("🔒 Acceso restringido. Por favor, identifícate con tu cuenta autorizada de Google.")
        if st.button("🔴 SIGN IN WITH GOOGLE", use_container_width=True, type="primary"):
            # Flujo de simulación. Al desplegar se integra con st.secrets["google_oauth"]
            st.session_state.autenticado = True
            st.session_state.usuario_email = "rrodriguez@miamigov.com"
            st.success("¡Autenticado con éxito!")
            st.rerun()

if not st.session_state.autenticado:
    login_pantalla()
    st.stop()

# ==========================================
# CUERPO DE LA APLICACIÓN (USUARIO VALIDADO)
# ==========================================
if st.button("🚪 Logout"):
    st.session_state.autenticado = False
    st.session_state.usuario_email = None
    st.rerun()

st.title("🗓️ Master Schedule Board (Live Cloud DB)")
st.write(f"Sesión activa: **{st.session_state.usuario_email}**")

# Inicializar dataset de empleados en sesión
if 'empleados' not in st.session_state:
    st.session_state.empleados = [
        {"name": "Barry", "lastname": "Tucker", "role": "Pool Supervisor", "phone": "305-555-0192", "email": "btucker@miamigov.com"},
        {"name": "Romina", "lastname": "Berdun", "role": "Aquatic Specialist", "phone": "305-555-0143", "email": "rberdun@miamigov.com"},
        {"name": "Rocco", "lastname": "Moreno", "role": "Lifeguard II", "phone": "305-555-0111", "email": "rmoreno@miamigov.com"},
        {"name": "Frank", "lastname": "Fernandez", "role": "Lifeguard II", "phone": "305-555-0122", "email": "ffernandez@miamigov.com"},
        {"name": "Rafael", "lastname": "Rodriguez", "role": "Lifeguard II", "phone": "305-555-0155", "email": "rrodriguez@miamigov.com"},
        {"name": "Noam", "lastname": "Reeve", "role": "Seasonal Lifeguard II", "phone": "305-555-0177", "email": "nreeve@miamigov.com"},
        {"name": "Daymi", "lastname": "Gonzalez", "role": "WSI", "phone": "305-555-0188", "email": "dgonzalez@miamigov.com"},
        {"name": "Kevin", "lastname": "Antia", "role": "WSI", "phone": "305-555-0199", "email": "kantia@miamigov.com"},
        {"name": "Stephanie", "lastname": "Kleiban", "role": "WSI", "phone": "305-555-0133", "email": "skleiban@miamigov.com"},
        {"name": "Miles", "lastname": "Rover", "role": "WSI", "phone": "305-555-0166", "email": "mrover@miamigov.com"},
        {"name": "Ashley", "lastname": "Valle", "role": "LG1", "phone": "305-555-0211", "email": "avalle@miamigov.com"},
        {"name": "Adrianna", "lastname": "Crivelli", "role": "Collection Clerk", "phone": "305-555-0222", "email": "acrivelli@miamigov.com"},
    ]

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
rotations = ["AM Rotation", "PM Rotation", "Noon Rotation", "All Day"]
locations = ["Grapeland", "Miller", "Shenandoah", "Gibson", "Range", "Jose Marti", "Curtis", "Manolo Reyes", "Virrick", "Williams"]
horas_validadas = ["05:00 AM", "05:30 AM", "06:00 AM", "06:30 AM", "07:00 AM", "07:30 AM", "08:00 AM", "08:30 AM", "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM", "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM", "07:30 PM", "08:00 PM", "08:30 PM", "09:00 PM", "09:30 PM", "10:00 PM"]

if 'matriz_horario' not in st.session_state:
    st.session_state.matriz_horario = {}

for emp in st.session_state.empleados:
    full_id = f"{emp['name']} {emp['lastname']}"
    if full_id not in st.session_state.matriz_horario:
        st.session_state.matriz_horario[full_id] = {day: {"rotation": "OFF", "hours": "", "location": "Shenandoah"} for day in days}

# ==========================================
# SIDEBAR: PANEL DE ADMINISTRACIÓN
# ==========================================
st.sidebar.header("📋 Administration Panel")

hoy_fecha = datetime.date.today()
dias_al_domingo = (hoy_fecha.weekday() + 1) % 7
domingo_periodo = hoy_fecha - datetime.timedelta(days=dias_al_domingo)
sabado_periodo = domingo_periodo + datetime.timedelta(days=6)
numero_semana = domingo_periodo.isocalendar()[1]
formato_semana_defecto = f"Week {numero_semana} ({domingo_periodo.strftime('%B %d')} - {sabado_periodo.strftime('%B %d, %Y')})"

semana_activa = st.sidebar.text_input("Active Schedule Week", formato_semana_defecto)

# 1. Manage Staff Members (CRUD)
with st.sidebar.expander("👤 1. Manage Staff Members (CRUD)", expanded=False):
    crud_mode = st.radio("Action", ["Add New", "Edit Existing", "Delete"], horizontal=True)
    if crud_mode == "Add New":
        in_name = st.text_input("First Name")
        in_last = st.text_input("Last Name")
        in_role = st.selectbox("Official Role", ["Pool Supervisor", "Aquatic Specialist", "Lifeguard II", "Seasonal Lifeguard II", "WSI", "LG1", "Collection Clerk"])
        in_phone = st.text_input("Phone Number")
        in_email = st.text_input("Email Address")
        if st.button("💾 Save New Guard"):
            if in_name.strip() and in_last.strip():
                full_key = f"{in_name.strip()} {in_last.strip()}"
                st.session_state.empleados.append({"name": in_name.strip(), "lastname": in_last.strip(), "role": in_role, "phone": in_phone.strip(), "email": in_email.strip()})
                st.session_state.matriz_horario[full_key] = {day: {"rotation": "OFF", "hours": "", "location": "Shenandoah"} for day in days}
                st.success("Registered!")
                st.rerun()

# INTERCAMBIO CON LA NUBE: 2. Database History Menu (Guardar y cargar de Supabase)
with st.sidebar.expander("🗄️ 2. Database History Menu (Cloud Live)", expanded=False):
    if st.button("💾 Save Week to Cloud DB"):
        # Eliminamos registros anteriores de esta misma semana para sobreescribir de forma limpia
        supabase.table("asignaciones").delete().eq("semana", semana_activa).execute()
        
        filas_a_insertar = []
        for emp in st.session_state.empleados:
            f_id = f"{emp['name']} {emp['lastname']}"
            for day in days:
                c = st.session_state.matriz_horario[f_id][day]
                filas_a_insertar.append({
                    "semana": semana_activa, "empleado": f_id, "rol": emp["role"],
                    "dia": day, "rotation": c["rotation"], "hours": c["hours"], "location": c["location"]
                })
        
        # Inserción masiva en la nube
        if filas_a_insertar:
            supabase.table("asignaciones").insert(filas_a_insertar).execute()
        st.success(f"¡Semana {semana_activa} respaldada en la nube!")

    st.write("---")
    try:
        # Consultar semanas disponibles en la nube de forma única
        response_semanas = supabase.table("asignaciones").select("semana").execute()
        lista_semanas = list(set([item['semana'] for item in response_semanas.data])) if response_semanas.data else []
        
        if lista_semanas:
            semana_consultar = st.selectbox("Select Week to Load from Cloud", lista_semanas)
            if st.button("📂 Load Selected Week"):
                response_datos = supabase.table("asignaciones").eq("semana", semana_consultar).execute()
                
                for r in response_datos.data:
                    emp_name = r["empleado"]
                    d_name = r["dia"]
                    if emp_name in st.session_state.matriz_horario:
                        st.session_state.matriz_horario[emp_name][d_name] = {
                            "rotation": r["rotation"], "hours": r["hours"], "location": r["location"]
                        }
                st.success("¡Datos sincronizados desde la base de datos en la nube!")
                st.rerun()
        else:
            st.caption("No se encontraron registros históricos en Supabase.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

# 3. Individual Shift Management
with st.sidebar.expander("⏳ 3. Assign / Edit Individual Shift", expanded=True):
    current_staff_keys = [f"{e['name']} {e['lastname']}" for e in st.session_state.empleados]
    if current_staff_keys:
        selected_emp = st.selectbox("Select Staff Member", current_staff_keys)
        selected_day = st.selectbox("Select Day", days)
        current_data = st.session_state.matriz_horario[selected_emp][selected_day]
        selected_rot = st.selectbox("Shift / Rotation", rotations)
        col_start, col_end = st.columns(2)
        with col_start: start_time = st.selectbox("Start Time", horas_validadas, index=7)
        with col_end: end_time = st.selectbox("End Time", horas_validadas, index=25)
        selected_loc = st.selectbox("Individual Location", locations, index=locations.index(current_data['location']))
        mark_off = st.checkbox("Mark Employee as OFF Duty")

        if st.button("📌 Apply / Update Assignment"):
            if mark_off:
                st.session_state.matriz_horario[selected_emp][selected_day] = {"rotation": "OFF", "hours": "", "location": selected_loc}
            else:
                st.session_state.matriz_horario[selected_emp][selected_day] = {"rotation": selected_rot, "hours": f"{start_time} - {end_time}", "location": selected_loc}
            st.success("Updated!")
            st.rerun()

# 4. Staff Count Metrics
with st.sidebar.expander("📊 4. Staff Count Metrics", expanded=False):
    metric_day = st.selectbox("View Metrics For Day:", days)
    columnas_reporte = ["AM Rotation", "PM Rotation", "Noon Rotation", "All Day", "OFF"]
    roles_sistema = ["Pool Supervisor", "Aquatic Specialist", "Lifeguard II", "Seasonal Lifeguard II", "WSI", "LG1", "Collection Clerk"]
    matrix_metrics = {role: {col: 0 for col in columnas_reporte} for role in roles_sistema}
    for emp in st.session_state.empleados:
        f_id = f"{emp['name']} {emp['lastname']}"
        role = emp["role"]
        if f_id in st.session_state.matriz_horario:
            status_rotation = st.session_state.matriz_horario[f_id][metric_day]["rotation"]
            if status_rotation in matrix_metrics[role]: matrix_metrics[role][status_rotation] += 1
            else: matrix_metrics[role]["OFF"] += 1
    df_metrics_detailed = pd.DataFrame.from_dict(matrix_metrics, orient='index')
    df_totales_metrics = df_metrics_detailed.sum(axis=0).to_frame().T
    df_totales_metrics.index = ["TOTAL STAFF"]
    st.dataframe(pd.concat([df_metrics_detailed, df_totales_metrics]), use_container_width=True)

# ==========================================
# AUTOMATED MINIMUM REQUIREMENTS ENGINE
# ==========================================
st.subheader("⚡ Automated Minimum Requirements Scheduler")
if st.button("⚡ COMPLETE SCHEDULE AUTOMATICALLY", type="primary"):
    for day in days:
        supervisors = [f"{e['name']} {e['lastname']}" for e in st.session_state.empleados if e["role"] == "Pool Supervisor"]
        specialists = [f"{e['name']} {e['lastname']}" for e in st.session_state.empleados if e["role"] == "Aquatic Specialist"]
        guards = [f"{f['name']} {f['lastname']}" for f in st.session_state.empleados if "Lifeguard" in f["role"] or "LG1" in f["role"]]
        wsis = [f"{w['name']} {w['lastname']}" for w in st.session_state.empleados if w["role"] == "WSI"]

        if not [sp for sp in specialists if st.session_state.matriz_horario[sp][day]["rotation"] != "OFF"] and specialists:
            st.session_state.matriz_horario[random.choice(specialists)][day] = {"rotation": "All Day", "hours": "08:30 AM - 05:30 PM", "location": "Shenandoah"}
        avail_sup = [su for su in supervisors if st.session_state.matriz_horario[su][day]["rotation"] == "OFF"]
        if len(avail_sup) >= 2:
            for su in random.sample(avail_sup, 2): st.session_state.matriz_horario[su][day] = {"rotation": "AM Rotation", "hours": "05:30 AM - 02:00 PM", "location": "Shenandoah"}
        avail_wsi = [w for w in wsis if st.session_state.matriz_horario[w][day]["rotation"] == "OFF"]
        if len(avail_wsi) >= 3:
            for w in random.sample(avail_wsi, 3): st.session_state.matriz_horario[w][day] = {"rotation": "Noon Rotation", "hours": "12:00 PM - 04:30 PM", "location": "Shenandoah"}
        avail_g = [g for g in guards if st.session_state.matriz_horario[g][day]["rotation"] == "OFF"]
        if len(avail_g) >= 3:
            for g in random.sample(avail_g, 3): st.session_state.matriz_horario[g][day] = {"rotation": "PM Rotation", "hours": "01:00 PM - 09:30 PM", "location": "Shenandoah"}
    st.success("Automated requirements met!")
    st.rerun()

# ==========================================
# MASTER MATRIX DESIGN WITH COLUMN TOTALS
# ==========================================
html_styles = """
<style>
    .schedule-table { width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 11px; margin-top: 10px; }
    .schedule-table th { background-color: #f1f3f4; padding: 6px; border: 1px solid #dae0e5; text-align: center; font-weight: bold; color: #3c4043; }
    .schedule-table td { padding: 8px 4px; border: 1px solid #dae0e5; vertical-align: top; text-align: center; line-height: 1.3; }
    .shift-box { font-weight: bold; color: #137333; margin-bottom: 2px; }
    .loc-box { font-style: italic; color: #b06000; font-weight: bold; }
    .total-row { background-color: #e8f0fe; font-weight: bold; color: #1a73e8; }
</style>
"""
st.markdown(html_styles, unsafe_allow_html=True)

html_table = f"""
<div style="width:100%;">
    <h2 style="text-align:center; font-family:Arial;">Shenandoah Park Aquatic Facility</h2>
    <h4 style="text-align:center; font-family:Arial; color:#555; margin-top:0;">Master Staff Schedule — {semana_activa}</h4>
    <table class="schedule-table">
        <thead><tr><th>Role</th><th>Name</th>{"".join([f"<th>{day}</th>" for day in days])}<th>Hours</th></tr></thead><tbody>
"""

totales_por_dia = {day: 0 for day in days}
gran_total_horas = 0

for emp in st.session_state.empleados:
    f_id = f"{emp['name']} {emp['lastname']}"
    if f_id in st.session_state.matriz_horario:
        html_table += f'<tr><td style="font-weight:bold; color:#1a73e8; text-align:left;">{emp["role"]}</td><td style="font-weight:bold; text-align:left;">{f_id}</td>'
        tot_horas_empleado = 0
        for day in days:
            cell = st.session_state.matriz_horario[f_id][day]
            if cell["rotation"] == "OFF": html_table += '<td style="color:#9aa0a6; background:#f8f9fa; vertical-align:middle;">OFF</td>'
            else:
                html_table += f'<td><div class="shift-box">{cell["rotation"]}</div><div>{cell["hours"]}</div><div class="loc-box">@ {cell["location"]}</div></td>'
                tot_horas_empleado += 8
                totales_por_dia[day] += 1
        html_table += f'<td style="font-weight:bold; vertical-align:middle;">{tot_horas_empleado}</td></tr>'
        gran_total_horas += tot_horas_empleado

html_table += f'<tr class="total-row"><td colspan="2" style="text-align:right; padding-right:15px;">Total Active Staff</td>'
for day in days: html_table += f'<td>{totales_por_dia[day]} Staff</td>'
html_table += f'<td>{gran_total_horas} Hrs</td></tr></tbody></table></div>'

st.markdown(html_table, unsafe_allow_html=True)

html_imprimible_completo = f"<!DOCTYPE html><html><head><title>Print</title>{html_styles}</head><body onload='window.print();'>{html_table}</body></html>"

st.write("")
col_btn1, col_btn2 = st.columns([5, 1])
with col_btn1: st.download_button(label="📥 DOWNLOAD WEEKLY MATRIX (HTML)", data=html_imprimible_completo, file_name=f"Schedule_{semana_activa.replace(' ', '_')}.html", mime="text/html")
with col_btn2: st.download_button(label="🖨️ OPEN PRINT PREVIEW", data=html_imprimible_completo, file_name="print_preview.html", mime="text/html", use_container_width=True)