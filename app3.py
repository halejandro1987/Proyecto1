import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np

# Función para obtener el tipo de archivo
def get_file_type(uploaded_file):
    if uploaded_file is not None:
        file_name, file_extension = uploaded_file.name, uploaded_file.type
        if file_extension == "text/csv":
            return "csv"
        elif file_extension in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            return "Excel"
        else:
            return "Otro, por favor subir csv o Excel"
    else:
        return "Ninguno, esperando el archivo..."

# Función para clasificar variables
def classify_variables(dataset):
    categoricas = []
    continuas = []
    discretas = []
    fecha = []
    for col in dataset.columns:
        if pd.api.types.is_string_dtype(dataset[col]):
            categoricas.append(col)
        elif pd.api.types.is_numeric_dtype(dataset[col]):
            if pd.api.types.is_float_dtype(dataset[col]):
                continuas.append(col)
            else:
                discretas.append(col)
        elif pd.api.types.is_datetime64_any_dtype(dataset[col]):
            fecha.append(col)
    return categoricas, continuas, discretas, fecha

# Función para mostrar información descriptiva y gráficas
def show_descriptive_info(tab, dataset, variable, variable_type):
    if variable_type == 'categoricas':
        fig = plt.figure(figsize=(10, 4))
        sns.countplot(x=variable, data=dataset)
        plt.title(f"Conteo de {variable}")
        tab.pyplot(fig)
    else:
        desc = dataset[variable].describe()
        tab.write(desc)
        fig = plt.figure(figsize=(10, 4))
        if variable_type == 'continuas':
            sns.kdeplot(dataset[variable], fill=True)
            plt.title(f"Densidad de {variable}")
        elif variable_type == 'discretas':
            sns.histplot(dataset[variable], kde=False)
            plt.title(f"Histograma de {variable}")
        tab.pyplot(fig)

def main():
    st.set_page_config(page_title="Análisis de Datos")
    st.write("# Proyecto: Análisis de Datos")

    tab0, tab1 = st.tabs(["Carga de Datos", "Análisis de Datos"])

    if tab0:
        tab0.title("Cargar Datos")
        uploaded_file = tab0.file_uploader("Subir archivo", type=["csv", "xlsx"])
        file_type = get_file_type(uploaded_file)
        tab0.write(f"Tipo de Archivo: {file_type}")

        dataset = pd.DataFrame()
        if file_type == "csv":
            dataset = pd.read_csv(uploaded_file)
        elif file_type == "Excel":
            dataset = pd.read_excel(uploaded_file)

        if not dataset.empty:
            tab0.write("Vista previa de los datos:")
            tab0.dataframe(dataset.head())

    if tab1:
        if dataset.empty:
            tab1.write("Por favor, carga los datos en la pestaña 'Carga de Datos'")
        else:
            tab1.title("Análisis de Datos")
            categoricas, continuas, discretas, fecha = classify_variables(dataset)

            tab1.write("Variables Categóricas: ", categoricas)
            tab1.write("Variables Continuas: ", continuas)
            tab1.write("Variables Discretas: ", discretas)
            tab1.write("Variables Fecha: ", fecha)

            selected_variable = tab1.selectbox("Seleccione una variable para análisis descriptivo:", dataset.columns)
            variable_type = ""
            if selected_variable in categoricas:
                variable_type = 'categoricas'
            elif selected_variable in continuas:
                variable_type = 'continuas'
            elif selected_variable in discretas:
                variable_type = 'discretas'

            show_descriptive_info(tab1, dataset, selected_variable, variable_type)

if __name__ == '__main__':
    main()
