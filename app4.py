import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
import numpy as np
from statsmodels.graphics.mosaicplot import mosaic

# Función para obtener el tipo de archivo
def get_file_type(uploaded_file):
    if uploaded_file is not None:
        file_name = uploaded_file.name
        if file_name.endswith('.csv'):
            return "csv"
        elif file_name.endswith('.xls') or file_name.endswith('.xlsx'):
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

# Función para calcular el coeficiente de contingencia de Cramer
def cramer_v(x, y):
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    return (chi2 / (n * (min(confusion_matrix.shape) - 1))) ** 0.5

# Función para gráficas combinadas
def combined_graphs(tab, dataset, categoricas, continuas, discretas, fecha):
    tab.write("### Gráficas Combinadas de Dos Variables")
    variable_type1 = tab.selectbox("Seleccione el tipo de la primera variable:", ["Continua/Discreta", "Temporal", "Categórica"])
    variable_type2 = tab.selectbox("Seleccione el tipo de la segunda variable:", ["Continua/Discreta", "Temporal", "Categórica"])

    if variable_type1 == "Continua/Discreta" and variable_type2 == "Continua/Discreta":
        var1 = tab.selectbox("Seleccione la primera variable numérica:", continuas + discretas)
        var2 = tab.selectbox("Seleccione la segunda variable numérica:", continuas + discretas)
        fig, ax = plt.subplots()
        sns.scatterplot(x=dataset[var1], y=dataset[var2], ax=ax)
        correlation = dataset[[var1, var2]].corr().iloc[0, 1]
        tab.pyplot(fig)
        tab.write(f"Correlación entre {var1} y {var2}: {correlation}")

    elif variable_type1 == "Continua/Discreta" and variable_type2 == "Temporal":
        var1 = tab.selectbox("Seleccione la variable numérica:", continuas + discretas)
        var2 = tab.selectbox("Seleccione la variable temporal:", fecha)
        fig, ax = plt.subplots()
        sns.lineplot(x=dataset[var2], y=dataset[var1], ax=ax)
        tab.pyplot(fig)

    elif variable_type1 == "Categórica" and variable_type2 == "Continua/Discreta":
        var1 = tab.selectbox("Seleccione la variable categórica:", categoricas)
        var2 = tab.selectbox("Seleccione la variable continua/discreta:", continuas + discretas)
        fig, ax = plt.subplots()
        sns.boxplot(x=dataset[var1], y=dataset[var2], ax=ax)
        tab.pyplot(fig)

    elif variable_type1 == "Categórica" and variable_type2 == "Categórica":
        var1 = tab.selectbox("Seleccione la primera variable categórica:", categoricas)
        var2 = tab.selectbox("Seleccione la segunda variable categórica:", categoricas)
        fig, ax = plt.subplots(figsize=(10, 6))
        mosaic(dataset, [var1, var2], ax=ax)
        plt.title(f"Mosaico de {var1} vs {var2}")
        tab.pyplot(fig)
        cramer_value = cramer_v(dataset[var1], dataset[var2])
        tab.write(f"Coeficiente de Contingencia de Cramer entre {var1} y {var2}: {cramer_value}")

# Función principal
def main():
    st.set_page_config(page_title="Análisis de Datos")
    st.write("# Proyecto: Análisis de Datos")

    tab0, tab1, tab2 = st.tabs(["Carga de Datos", "Análisis de Datos", "Gráficas Combinadas"])

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

            tab1.write("Variables Categóricas: " + ', '.join(categoricas))
            tab1.write("Variables Continuas: " + ', '.join(continuas))
            tab1.write("Variables Discretas: " + ', '.join(discretas))
            tab1.write("Variables Fecha: " + ', '.join(fecha))

            selected_variable = tab1.selectbox("Seleccione una variable para análisis descriptivo:", dataset.columns)
            variable_type = ""
            if selected_variable in categoricas:
                variable_type = 'categoricas'
            elif selected_variable in continuas:
                variable_type = 'continuas'
            elif selected_variable in discretas:
                variable_type = 'discretas'

            show_descriptive_info(tab1, dataset, selected_variable, variable_type)

    if tab2:
        if dataset.empty:
            tab2.write("Por favor, carga los datos en la pestaña 'Carga de Datos'")
        else:
            combined_graphs(tab2, dataset, categoricas, continuas, discretas, fecha)

if __name__ == '__main__':
    main()
