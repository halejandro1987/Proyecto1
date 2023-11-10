import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats

# Cargar del archivo
def load_data(file):
    if file is not None:
        if file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            dataset = pd.read_excel(file)
        else:
            dataset = pd.read_csv(file)
        return dataset
    return None

# Primera pestaña
def welcome_tab():
    st.title("Bienvenido a la Aplicación")
    st.write("Esta es la pestaña de bienvenida. Por favor, carga un archivo de datos en la pestaña siguiente.")

# Configurar la segunda pestaña
def analysis_tab(dataset):
    st.title("Análisis de Datos")
    st.dataframe(dataset)

    variable = st.selectbox("Variable", ['Customer_Age', 'Credit_Limit'])

    # Mínimo y máximo de la variable
    min = dataset[variable].min()
    max = dataset[variable].max()

    kde = stats.gaussian_kde(dataset[variable])
    rangos = st.slider(f"Valor de {variable}", min, max, (min, max))
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
    st.pyplot(fig)
    st.text(f"Probabilidad: {np.round(np.sum(y), 4) / 100}")

    categoricas = []
    for col in dataset.columns:
        if (dataset[col].dtype == 'object') or (dataset[col].dtype == 'string'):
            categoricas.append(col)

    continuas = []
    for col in dataset.columns:
        if (dataset[col].dtype == 'float64') or (dataset[col].dtype == 'int64'):
            continuas.append(col)

    fig2 = plt.figure(figsize=(10, 4))
    variableA = st.selectbox("Variable Continua", continuas)
    variableB = st.selectbox("Variable Discreta", categoricas)
    sns.boxplot(data=dataset, x=variableB, y=variableA)
    st.pyplot(fig2)

def main():
    st.set_page_config(page_title="Inicio")
    st.write("# Proyecto: Naomi Lara / Héctor Aragón / Jorge Yxcot")
    
    # Crear las pestañas
    tabs = st.tabs(["Bienvenida", "Análisis de Datos"])
    
    # Cargar datos en la segunda pestaña
    dataset = None
    if tabs[1]:
        st.sidebar.write("Carga un archivo de datos (.csv o .xlsx)")
        uploaded_file = st.sidebar.file_uploader("Subir archivo", type=["csv", "xlsx"])
        dataset = load_data(uploaded_file)

    if tabs[0]:
        welcome_tab()
    elif tabs[1]:
        analysis_tab(dataset)

if __name__ == '__main__':
    main()
