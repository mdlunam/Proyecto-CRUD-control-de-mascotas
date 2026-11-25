import os
from datetime import date

import pandas as pd
import streamlit as st

ARCHIVO = "mascotas.csv"
COLUMNAS = ["id", "nombre", "especie", "edad", "peso_kg", "comida", "vacunas_al_dia", "proxima_cita_vet", "notas"]


def cargar_datos():
    if os.path.exists(ARCHIVO):
        return pd.read_csv(ARCHIVO, dtype=str, keep_default_na=False)
    return pd.DataFrame(columns=COLUMNAS)


def guardar_datos(df):
    df.to_csv(ARCHIVO, index=False)


st.set_page_config(page_title="Mis mascotas", layout="wide")
st.title("Control de mis mascotas 🐾")
st.write("Aquí llevo el registro de mi perrita y mis gatos: comida, vacunas y citas/control con el veterinario.")

datos = cargar_datos()

opcion = st.sidebar.radio("¿Qué quieres hacer?", ["Ver mascotas", "Agregar mascota", "Editar mascota", "Eliminar mascota"])

if opcion == "Ver mascotas":
    st.subheader("Mis mascotas")
    if datos.empty:
        st.info("Todavía no hay mascotas registradas.")
    else:
        especie = st.selectbox("Filtrar por especie", ["Todas", "Perro", "Gato", "Otro"])
        if especie != "Todas":
            st.dataframe(datos[datos["especie"] == especie], hide_index=True)
        else:
            st.dataframe(datos, hide_index=True)
        st.write(f"Total de mascotas: {len(datos)}")

elif opcion == "Agregar mascota":
    st.subheader("Agregar una mascota")
    with st.form("form_agregar", clear_on_submit=True):
        nombre = st.text_input("Nombre")
        especie = st.selectbox("Especie", ["Perro", "Gato", "Otro"])
        edad = st.number_input("Edad (años)", min_value=0, max_value=30, step=1)
        peso = st.number_input("Peso (kg)", min_value=0.0, step=0.5)
        comida = st.text_input("Comida que come")
        vacunas = st.selectbox("¿Vacunas al día?", ["Sí", "No"])
        cita = st.date_input("Próxima cita al veterinario", value=date.today())
        notas = st.text_area("Notas")
        guardar = st.form_submit_button("Guardar")

    if guardar:
        if nombre.strip() == "":
            st.error("El nombre es obligatorio.")
        else:
            nuevo_id = 1 if datos.empty else datos["id"].astype(int).max() + 1
            valores = [nuevo_id, nombre, especie, edad, peso, comida, vacunas, cita, notas]
            nueva = pd.DataFrame([[str(v) for v in valores]], columns=COLUMNAS)
            datos = pd.concat([datos, nueva], ignore_index=True)
            guardar_datos(datos)
            st.success(f"{nombre} quedó registrada.")

elif opcion == "Editar mascota":
    st.subheader("Editar una mascota")
    if datos.empty:
        st.info("No hay mascotas para editar.")
    else:
        elegida = st.selectbox("Elige la mascota", datos["nombre"] + " (id " + datos["id"].astype(str) + ")")
        id_elegido = int(elegida.split("id ")[1].replace(")", ""))
        fila = datos[datos["id"] == str(id_elegido)].iloc[0]
        especies = ["Perro", "Gato", "Otro"]

        with st.form("form_editar"):
            nombre = st.text_input("Nombre", value=fila["nombre"])
            especie = st.selectbox("Especie", especies, index=especies.index(fila["especie"]))
            edad = st.number_input("Edad (años)", min_value=0, max_value=30, step=1, value=int(float(fila["edad"])))
            peso = st.number_input("Peso (kg)", min_value=0.0, step=0.5, value=float(fila["peso_kg"]))
            comida = st.text_input("Comida que come", value=str(fila["comida"]))
            vacunas = st.selectbox("¿Vacunas al día?", ["Sí", "No"], index=0 if fila["vacunas_al_dia"] == "Sí" else 1)
            cita = st.date_input("Próxima cita al veterinario", value=pd.to_datetime(fila["proxima_cita_vet"]).date())
            notas = st.text_area("Notas", value=fila["notas"])
            actualizar = st.form_submit_button("Guardar cambios")

        if actualizar:
            valores = [nombre, especie, edad, peso, comida, vacunas, cita, notas]
            datos.loc[datos["id"] == str(id_elegido), COLUMNAS[1:]] = [str(v) for v in valores]
            guardar_datos(datos)
            st.success(f"Se actualizaron los datos de {nombre}.")

elif opcion == "Eliminar mascota":
    st.subheader("Eliminar una mascota")
    if datos.empty:
        st.info("No hay mascotas para eliminar.")
    else:
        elegida = st.selectbox("Elige la mascota", datos["nombre"] + " (id " + datos["id"].astype(str) + ")")
        id_elegido = int(elegida.split("id ")[1].replace(")", ""))
        confirmar = st.checkbox("Sí, quiero eliminar esta mascota")
        if st.button("Eliminar"):
            if confirmar:
                datos = datos[datos["id"] != str(id_elegido)]
                guardar_datos(datos)
                st.success("Mascota eliminada.")
            else:
                st.warning("Marca la casilla para confirmar.")
