# Modi Lipi Intelligence System 🏛️📜

An advanced AI-driven platform for preserving and interpreting the historic **Modi Lipi** script. This system combines Deep Learning OCR, linguistic post-processing, and interactive historical exploration to bridge the gap between ancient records and modern understanding.

## 🚀 Key Features

- **📜 Script Translator**: Real-time translation from Modi Lipi to Devanagari (Marathi) using high-accuracy mapping.
- **👁️ Deep Learning OCR**: A CRNN-based Optical Character Recognition engine trained to identify complex Modi characters.
- **✍️ Marathi Text Correction**: Intelligent post-processing layer using Levenshtein distance for refining OCR outputs.
- **🗺️ Heritage Explorer**: Interactive dashboard featuring 30+ heritage sites with historical insights and mapping.
- **✨ Magic Wand AI**: AI-driven insights for historical artifacts and script interpretation.

## 🛠️ Technology Stack

- **Backend**: Flask (Intelligence Dashboard) & Streamlit (Translator Interface)
- **OCR Engine**: PyTorch / CRNN Architecture
- **NLP**: Custom phonetic mapping and Marathi dictionary correction
- **Frontend**: Responsive HTML5/CSS3 with Leaflet.js for interactive mapping
- **Data**: JSON-based historical site database

## 📦 Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/modi-lipi-intelligence.git
   cd modi-lipi-intelligence
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Applications**:
   - **Main Dashboard (Flask)**: `python app.py`
   - **Script Translator (Streamlit)**: `streamlit run streamlit_app.py`

## 📂 Project Structure

- `app.py`: Main Flask server for the heritage dashboard.
- `streamlit_app.py`: Interactive script translator UI.
- `crnn_model.py`: Neural network architecture for character recognition.
- `translator/`: Core logic for script conversion.
- `marathi_corrector.py`: Text refinement and spell-check layer.
- `data/`: Datasets and historical metadata.

## 🤝 Contributing

Contributions are welcome! If you'd like to improve the OCR accuracy or add more heritage sites, please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
