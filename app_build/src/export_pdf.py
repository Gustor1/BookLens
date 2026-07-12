"""
BookLens — Export PDF
Génère un fichier PDF à partir d'une liste de recommandations.
"""

from fpdf import FPDF
import io
import datetime

class PDFReport(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Helvetica', 'B', 15)
        # Title
        self.cell(0, 10, 'BookLens - Rapport de Recommandations', 0, 1, 'C')
        # Line break
        self.ln(5)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Helvetica', 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_recommendations_pdf(source_book, recs_df):
    """
    Génère un PDF en mémoire et retourne le buffer (bytes).
    """
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Titre du rapport
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, f"Source : {source_book}", 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 10, f"Date de l'export : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
    pdf.ln(5)
    
    # Tableau des résultats
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_fill_color(200, 220, 255)
    
    # Header du tableau (largeurs : 10, 80, 40, 30, 30)
    pdf.cell(10, 10, '#', 1, 0, 'C', fill=True)
    pdf.cell(80, 10, 'Titre', 1, 0, 'C', fill=True)
    pdf.cell(50, 10, 'Auteur', 1, 0, 'C', fill=True)
    pdf.cell(25, 10, 'Score', 1, 0, 'C', fill=True)
    pdf.cell(25, 10, 'Note', 1, 1, 'C', fill=True)
    
    pdf.set_font('Helvetica', '', 10)
    for i, row in recs_df.iterrows():
        # Clean title for PDF encoding
        title = str(row['Book-Title']).encode('latin-1', 'replace').decode('latin-1')
        if len(title) > 35:
            title = title[:32] + "..."
            
        author = str(row.get('Author', 'Inconnu')).encode('latin-1', 'replace').decode('latin-1')
        if len(author) > 22:
            author = author[:19] + "..."
            
        score = f"{row.get('Similarity-Score', 0):.2f}"
        rating = f"{row.get('Avg-Rating', 0):.1f}/10"
        
        pdf.cell(10, 10, str(i+1), 1, 0, 'C')
        pdf.cell(80, 10, title, 1, 0, 'L')
        pdf.cell(50, 10, author, 1, 0, 'L')
        pdf.cell(25, 10, score, 1, 0, 'C')
        pdf.cell(25, 10, rating, 1, 1, 'C')

    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.cell(0, 10, "Généré par BookLens V3 - Modele Hybride (Collaboratif + Contenu)", 0, 1, 'C')

    # Exporter dans un buffer bytes
    return bytes(pdf.output(dest="S"))
