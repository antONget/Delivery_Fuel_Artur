from PyPDF2 import PdfReader, PdfWriter


async def search_receipt(receipt: str, personal_account: str) -> bool:
    """
    Поиск лицевого счета в файле
    :param receipt:
    :param personal_account:
    :return:
    """
    reader = PdfReader("utils/search.pdf")
    numpages = len(reader.pages)
    for page_number in range(0, numpages):
        page = reader.pages[page_number]
        text = page.extract_text()
        pdfWriter = PdfWriter()
        if receipt in text:  # changed here
            pdfWriter.add_page(reader.pages[page_number])
            with open(f'receipt/{personal_account}.pdf', 'wb') as f:
                pdfWriter.write(f)
                f.close()
            return True
    return False

if __name__ == '__main__':
    search_receipt()