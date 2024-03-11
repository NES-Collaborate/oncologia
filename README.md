# Oncology Management Application

Welcome to the Oncology Management Application, a comprehensive solution designed to streamline the management of oncological patients at the GHC Clinical Center. Developed by a team of dedicated students and collaborators from [NES (Novo Ensino Suplementar)](https://novoensinosuplementar.com), this application addresses the challenges presented during the FGV Workshop of Mathematical Problems, focusing on the needs of the Oncological GHC Center.

## Key Features

### Authentication Protection

To ensure data security, the application requires user authentication for access, safeguarding sensitive patient information.

### Patient Management

Efficiently manage patient data within the database, including the ability to create, view, update, and assign status to patients. The user-friendly interface allows for easy data retrieval, with the option to download data using intuitive column names. Additionally, users can search for patients by GHC number, name, birthday, and status, as well as filter patients by different statuses.

### Task Management

Stay organized by scheduling tasks for patients and receive timely notifications when tasks are due, ensuring that critical patient care activities are never overlooked.

### Data Visualization

Visualize patient data through interactive graphs, providing valuable insights for healthcare professionals.

## Development Team

This application has been meticulously developed and is continuously maintained by NES students, along with contributions from dedicated collaborators:

- Felipe Adeildo - [@felipe-adeildo](https://github.com/felipe-adeildo)
- Arthur Rabello - [@arthurabello](https://github.com/arthurabello) 
- Luiz Antônio
- Other NES collaborators, including Edeilson Costa [@ecaf1]

## Getting Started

To use the Oncology Management Application, ensure you meet the following requirements:

- Python 3 (Version 3.10 or newer)
- Python requirements

### Installing Python Requirements

```bash
pip3 install -r requirements.txt
```

### Running the Application

**Linux**:

1. Create the schema and credentials file:

```bash
make init-db # It will create a credentials.json
```

2. Run the application:

```bash
make server
```

**Windows**:

1. Create the schema:

```bash
python -m flask init-db
python generate_default_values.py # Optional
```

2. Run the application:

```bash
python -m flask run
```

### Adding "Fake" Data from a CSV File (Developed in the Workshop)

To populate the application with sample data, you'll need a CSV file located at `data/data_oncology.csv` with the following columns:

`*,Idade,Sexo,GRUPO DE TUMOR,LOCAL,Data Entrada GHC,Porta de Entrada,Equipe de Entrada,Data Diagnóstico,Diagnóstico Interno / Externo,Data 1º Tratamento,GHC/FORA,Equipe tratamento,Tempo de chegada no GHC,Tempo de TTO,Lei 60 dias,Tipo de Procedimento,Procedimento,Tempo RDT`

Run the following command to add the sample data:

```bash
python generate_fake_data.py
```

Experience the power of the Oncology Management Application in simplifying patient care and improving oncological data management.
