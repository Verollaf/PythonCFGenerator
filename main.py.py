import pandas as pd
from gender_guesser.detector import Detector
from codicefiscale import codicefiscale

# Funzione per calcolare il sesso basandosi sul nome
def calcola_sesso(nome):
    detector = Detector()
    sesso = detector.get_gender(nome.split()[0])  # Usa il primo nome
    if sesso in ['male', 'mostly_male']:
        return 'M'
    elif sesso in ['female', 'mostly_female']:
        return 'F'
    return 'ND'  # Non determinato

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

def main():
    # Leggere il file Excel
    input_path = "data/input.xlsx"
    output_path = "data/output.xlsx"
    
    print("Caricamento del file di input...")
    df = pd.read_excel(input_path)
    
    # Calcolare il sesso
    print("Calcolo del sesso...")
    df['Sesso'] = df['Nome'].apply(calcola_sesso)
    
    # Generare il codice fiscale
    print("Generazione del codice fiscale...")
    df['Codice Fiscale'] = df.apply(genera_codice_fiscale, axis=1)
    
    # Scrivere il risultato in un nuovo file Excel
    print("Scrittura del file di output...")
    df.to_excel(output_path, index=False)
    print(f"Operazione completata! File salvato in: {output_path}")

if __name__ == "__main__":
    main()
