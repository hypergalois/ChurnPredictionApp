import streamlit as st
import pandas as pd
import os
import pickle
import json
from utils import transform_data
from matplotlib import pyplot as plt
import seaborn as sns

st.title('Predecir Abandono de Clientes 🚀')
st.write('¡Haz clic en Predecir para determinar si es probable que tu cliente abandone!')

with open('schema.json', 'r') as f:
    schema = json.load(f)
# st.write(schema)

column_order_in = list(schema['column_info'].keys())[:-1]
column_order_out = list(schema['transformed_columns']['transformed_columns'])
# st.write(column_order_out)

# Sidebar Section
st.sidebar.info("¡Actualiza estas características!")
# Collect the input features
options = {}
for column, column_properties in schema['column_info'].items():
    if column == 'churn':
        pass
    elif column_properties['dtype'] == 'int64' or column_properties['dtype'] == 'float64':
        min_val, max_val = column_properties['values']
        data_type = column_properties['dtype']

        feature_mean = (min_val + max_val) / 2
        if data_type == 'int64':
            feature_mean = int(feature_mean)

        options[column] = st.sidebar.slider(column, min_val, max_val, value=feature_mean)
    
    elif column_properties['dtype'] == 'object':
        options[column] = st.sidebar.selectbox(column, column_properties['values'])

# Load model and encoder
model_path = os.path.join('..', 'models', 'experiment-1', 'xg.pkl')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

encoder_path = os.path.join('..', 'models', 'experiment-1', 'encoder.pkl')
with open(encoder_path, 'rb') as f:
    onehot = pickle.load(f)

mean_eve_mins = 200.29

# st.write(options)

# Make our predictions
if st.button('Predecir'):
    # Convert options to df
    scoring_data = pd.Series(options).to_frame().T
    scoring_data = scoring_data[column_order_in]
    

    # Check datatypes
    for column, column_properties in schema['column_info'].items():
        if column != 'churn':
            dtype = column_properties['dtype']
            scoring_data[column] = scoring_data[column].astype(dtype)

    # st.write(scoring_data)

    # Apply data transformations
    scoring_sample = transform_data(scoring_data, column_order_out, mean_eve_mins, onehot)
    # st.write(scoring_sample)

    # Render Predictions
    prediction = model.predict(scoring_sample)
    st.write('Resultado:')

    if prediction[0] == 0:  # We use prediction[0] because prediction is an array
        st.write('¡El cliente se queda! 🔥🤩')
    else:
        st.write('El cliente se va... 💣😥')

    st.write('Detalles Cliente')
    st.write(options)


try:
    historical = pd.Series(options).to_frame().T
    historical['prediction'] = prediction
    if os.path.isfile('historical_data.csv'):
        historical.to_csv('historical_data.csv', mode='a', header=False, index=False)
    else:
        historical.to_csv('historical_data.csv', header=True, index=False)
except Exception as e:
    pass

st.header('Predicciones Históricas')
if os.path.isfile('historical_data.csv'):   
    hist = pd.read_csv('historical_data.csv')
    st.dataframe(hist)
    fig, ax = plt.subplots()
    sns.countplot(x='prediction', data=hist, ax=ax).set_title('Predicciones Históricas')
    st.pyplot(fig)
else:
    st.write('Sin datos históricos todavía.')