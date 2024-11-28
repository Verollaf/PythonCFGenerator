import pandas as pd
import streamlit as st
import gender_guesser.detector as gender
from codicefiscale import codicefiscale

# Funzione per calcolare il sesso basandosi sul nome
def calcola_sesso(nome):
    detector = gender.Detector()
    
    # Verifica che il nome sia valido
    if not isinstance(nome, str) or nome.strip() == "":
        return "Non valido"  # Non determinato per nomi vuoti o non validi
    
    # Estrai il primo nome
    primo_nome = nome.split()[0].capitalize()  # Usa il primo nome e capitalizza

    # Ottieni il sesso
    sesso = detector.get_gender(primo_nome)
    
    # Mappa il risultato a "M" (maschio), "F" (femmina) o "Non determinato"
    if sesso in ["male", "mostly_male"]:
        return "M"
    elif sesso in ["female", "mostly_female"]:
        return "F"
    else:
        return "Non determinato"

# Funzione per generare il codice fiscale
def genera_codice_fiscale(row):
    try:
        return codicefiscale.encode(
            surname=row['Cognome'],
            name=row['Nome'],
            sex=row['Sesso'],
            birthdate=row['Data di Nascita'],
            birthplace=row['Comune di Nascita']
        )
    except Exception as e:
        return f"Errore: {e}"

# Funzione principale dell'app
def main():
    st.title("Generatore Codice Fiscale")
    st.write("Carica un file Excel per iniziare")

    # Caricamento del file
    uploaded_file = st.file_uploader("Carica il file Excel", type=["xls", "xlsx"])
    if uploaded_file:
        # Leggere il file senza header
        df = pd.read_excel(uploaded_file, header=None)
        df.columns = df.columns.map(str)  # Convertire i nomi delle colonne in stringhe
        st.write("Anteprima del file caricato:")
        st.dataframe(df)

        # Selezionare le colonne
        st.write("Seleziona le colonne corrispondenti:")
        col_nome = st.selectbox("Colonna Nome:", df.columns)
        col_cognome = st.selectbox("Colonna Cognome:", df.columns)
        col_data_nascita = st.selectbox("Colonna Data di Nascita:", df.columns)
        col_comune_nascita = st.selectbox("Colonna Comune di Nascita:", df.columns)

        st.write("Colonna Nome selezionata:", col_nome)
        st.write("Colonna Cognome selezionata:", col_cognome)

        if st.button("Genera Codice Fiscale"):
            st.write("Elaborazione in corso...")

            # Creare un nuovo dataframe con i dati selezionati
            df.rename(columns={
                col_nome: "Nome",
                col_cognome: "Cognome",
                col_data_nascita: "Data di Nascita",
                col_comune_nascita: "Comune di Nascita"
            }, inplace=True)

            st.write("Colonne disponibili dopo il rinominamento:", df.columns.tolist())

            # Controllare che le colonne siano presenti
            if "Nome" not in df.columns or "Cognome" not in df.columns:
                st.error("Le colonne 'Nome' e 'Cognome' non sono state trovate. Assicurati di selezionarle correttamente.")
                return

            # Pulizia dei dati
            df['Nome'] = df['Nome'].fillna("").astype(str).str.strip()

            # Placeholder per il progresso e la tabella fissa
            progress_placeholder = st.empty()
            table_placeholder = st.empty()

            # Calcolare il sesso riga per riga con aggiornamenti incrementali
            for index, row in df.iterrows():
                sesso = calcola_sesso(row['Nome'])
                df.loc[index, 'Sesso'] = sesso

                # Aggiorna il progresso
                progress_placeholder.write(f"Calcolo del sesso in corso... Riga {index + 1} di {len(df)}")
                table_placeholder.dataframe(df.head(20))  # Mostra le prime 20 righe aggiornate

            # Generare il codice fiscale riga per riga con aggiornamenti incrementali
            for index, row in df.iterrows():
                cf = genera_codice_fiscale(row)
                df.loc[index, 'Codice Fiscale'] = cf

                # Aggiorna il progresso
                progress_placeholder.write(f"Generazione del codice fiscale in corso... Riga {index + 1} di {len(df)}")
                table_placeholder.dataframe(df.head(20))  # Mostra le prime 20 righe aggiornate

            # Mostrare i risultati finali
            progress_placeholder.empty()  # Rimuove il messaggio di progresso
            st.write("Elaborazione completata. Ecco i risultati finali:")
            table_placeholder.dataframe(df)

            # Scaricare il file elaborato
            output_file = "output.xlsx"
            df.to_excel(output_file, index=False)
            with open(output_file, "rb") as file:
                st.download_button(
                    label="Scarica il file elaborato",
                    data=file,
                    file_name="output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    main()
