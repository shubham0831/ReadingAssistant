import fitz 
from Prompts import prompts
import pyperclip
import Anthropic

def pdfToText(pdfPath):
    doc = fitz.open(pdfPath)

    text = ""
    for pageNum in range(100):
       page = doc[pageNum]
       text += page.get_text()
    # for page_num in range(doc.page_count):
    #     page = doc[page_num]
    #     text += page.get_text()

    doc.close()
    return text

# Example usage
pdfPath = "/Users/shubham/Code/personal/ReadingAssistant/apis/testpdfs/duneBook1.pdf"
# result_text = pdf_to_text(pdf_path)
# print(result_text)
pdfText = pdfToText(pdfPath)
samplePrompt = prompts["ChapterIdentifierPrompt"] + pdfText
singleLineText = ' '.join(samplePrompt.splitlines())
singleLineText = singleLineText.strip()
singleLineText = ' '.join(singleLineText.split())

client = Anthropic()
print(client.count_tokens(prompts["ChapterIdentifierPrompt"]))
# pyperclip.copy(singleLineText)