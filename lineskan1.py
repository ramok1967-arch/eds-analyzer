import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Konfiguracja strony
st.set_page_config(page_title="EDS Line Scan Analyzer", layout="wide")

st.title("🔬 EDS Line Scan Analyzer")
st.markdown("Upload your CSV file to generate professional, individual charts for each element.")

# 1. Panel boczny - Wczytywanie pliku
st.sidebar.header("Settings")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# Słownik domyślnych kolorów
default_colors = {
    'PdL': '#0000FF', 'AgL': '#808080', 'FeK': '#FF0000', 
    'NiK': '#008000', 'CuK': '#FFA500', 'ZnK': '#800080', 'SED': '#000000'
}

if uploaded_file is not None:
    try:
        # 2. Parsowanie danych
        content = uploaded_file.getvalue().decode('latin-1').splitlines()
        header_line = content[14].strip().split(',')
        header = [h.strip() for h in header_line]
        
        data = []
        for line in content[15:]:
            row = line.strip().split(',')
            if len(row) >= len(header):
                data.append(row[:len(header)])
        
        df = pd.DataFrame(data, columns=header)
        
        # Konwersja na liczby (bez ostrzeżeń)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(df[col])

        # Usuwamy kolumnę 'Point' z ramki danych (nie będzie potrzebna ani do tabeli, ani do wykresów)
        if 'Point' in df.columns:
            df = df.drop(columns=['Point'])

        # Wykrycie pierwiastków (teraz po usunięciu 'Point')
        cols = df.columns.tolist()
        idx_start = cols.index('Distance') + 1
        idx_end = cols.index('SED')
        elements = cols[idx_start:idx_end]

        # 3. Personalizacja kolorów w panelu bocznym
        st.sidebar.subheader("Element Colors")
        custom_colors = {}
        for el in elements:
            default_hex = default_colors.get(el, '#000000')
            custom_colors[el] = st.sidebar.color_picker(f"Color for {el}", default_hex)

        # 4. Wyświetlanie tabeli (Pełny zbiór danych z suwakiem)
        st.subheader("Data Preview")
        # st.dataframe bez .head() pokaże wszystkie wiersze w przewijanym oknie
        st.dataframe(df, use_container_width=True)
        st.info(f"The table above contains all {len(df)} data points. You can scroll, sort, and search.")

        # 5. Generowanie wykresów
        st.subheader("Generated Charts")
        
        for el in elements:
            # Styl wykresu (większe czcionki zgodnie z prośbą)
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(df['Distance'], df[el], color=custom_colors[el], linewidth=2)
            
            ax.set_title(f"Line Scan Profile: {el}", fontsize=18, fontweight='bold', pad=15)
            ax.set_xlabel("Distance [µm]", fontsize=14)
            ax.set_ylabel("Concentration [at.%]", fontsize=14)
            
            ax.tick_params(axis='both', which='major', labelsize=12)
            ax.grid(True, linestyle='--', alpha=0.6)
            
            # Wyświetlenie w Streamlit
            st.pyplot(fig)
            
            # Przycisk pobierania pod każdym wykresem
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300)
            st.download_button(
                label=f"Download {el} chart (PNG)", 
                data=buf.getvalue(), 
                file_name=f"Chart_{el}.png", 
                mime="image/png"
            )
            st.divider()

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload a CSV file in the sidebar to start analysis.")