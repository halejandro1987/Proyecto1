import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
import os



# Obtener Tipo de Archivo

def get_file_type(uploaded_file):
    if uploaded_file is not None:
        file_name, file_extension = uploaded_file.name, uploaded_file.type
        if file_extension == "text/csv":
            return "csv"
        elif file_extension in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            return "Excel"
        else:
            return "Otro, porfavor subir csv o Excel"
    else:
            return "Ninguno, esperando el archivo..."
    

# Configurar la segunda pestaña
def analysis_tab(dataset,tab):
    
    variable = tab.selectbox("Variable", ['Customer_Age', 'Credit_Limit'])

    # Mínimo y máximo de la variable
    min = dataset[variable].min()
    max = dataset[variable].max()

    kde = stats.gaussian_kde(dataset[variable])
    rangos = tab.slider(f"Valor de {variable}", min, max, (min, max))
    r_min = rangos[0]
    r_max = rangos[1]

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.kdeplot(dataset[variable], color="green", shade=True)

    kde_value_min = kde.evaluate(r_min)
    ax.vlines(x=r_min, ymin=0, ymax=kde_value_min)

    kde_value_max = kde.evaluate(r_max)
    ax.vlines(x=r_max, ymin=0, ymax=kde_value_max)

    x = np.linspace(r_min, r_max, 1000)
    y = kde.evaluate(x)
    ax.fill_between(x, y, color='orange', alpha=0.5)

    plt.title(f"Densidad de {variable}")
    tab.pyplot(fig)
    tab.text(f"Probabilidad: {np.round(np.sum(y), 4) / 100}")

    categoricas = []
    for col in dataset.columns:
        if (dataset[col].dtype == 'object') or (dataset[col].dtype == 'string'):
            categoricas.append(col)

    continuas = []
    for col in dataset.columns:
        if (dataset[col].dtype == 'float64') or (dataset[col].dtype == 'int64'):
            continuas.append(col)

    fig2 = plt.figure(figsize=(10, 4))
    variableA = tab.selectbox("Variable Continua", continuas)
    variableB = tab.selectbox("Variable Discreta", categoricas)
    sns.boxplot(data=dataset, x=variableB, y=variableA)
    tab.pyplot(fig2)


def main():
    st.set_page_config(page_title="Inicio")
    st.write("# Proyecto: Naomi Lara / Héctor Aragón / Jorge Yxcot")
    
    # Crear las pestañas
    tab0,tab1 = st.tabs(["Bienvenida", "Análisis de Datos"])
    
    # Cargar datos en la segunda pestaña
    
   
    if tab0:
        tab0.title("Bienvenido a la Aplicación")
        tab0.write("Esta es la pestaña de bienvenida. Por favor, carga un archivo de datos (.csv o .xlsx)")
        tab0.uploaded_file = tab0.file_uploader("", type=["csv", "xlsx"])
        tab0.tipo=get_file_type(tab0.uploaded_file)
        tab0.write(f"Tipo de Archivo: {tab0.tipo}")
   
    #dataframe vacio    
    dataset=pd.DataFrame()
    if tab0.tipo=="csv":
        dataset= pd.read_csv(tab0.uploaded_file)
    if tab0.tipo=="Excel":
        dataset= pd.read_excel(tab0.uploaded_file)

    elif tab1:
        if dataset.empty:
            tab1.write("Subir datos antes de mostrar analisis")
        else:
            tab1.title("Análisis de Datos")
            #al analisis se le manda el objeto tab que es donde se escribe la info de graficas
            tab1.write=analysis_tab(dataset,tab1)
            tab1.dataframe(dataset)

if __name__ == '__main__':
    main()
