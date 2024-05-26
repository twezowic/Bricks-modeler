import PyPDF2

def print_pdf_content(pdf_path):
    flaga = False
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            if (flaga is True or "6250591" in page.extract_text()):
                print(page.extract_text())
                flaga = True

pdf_file_path = 'instr.pdf'

print_pdf_content(pdf_file_path)