from openai import OpenAI
from backend.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def agent1_primary(context, question):
    """
    Primary reasoning agent — answers ANY type of question.
    Uses PDF context + general medical knowledge.
    """
    prompt = f"""
    You are a medical research assistant.
    Use the context extracted from the uploaded PDFs to answer the user's question.
    
    Context from documents:
    {context}

    User question:
    {question}

    Your task:
    - Understand the user's intent.
    - Provide the most relevant, accurate medical answer.
    - If helpful, summarize key findings.
    - If the question requires analysis (risks, symptoms, interpretations), perform it.
    - If the answer is not in the documents, state that clearly but give general medical insight.

    Produce a clear, structured response.
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


def agent2_validate(final_answer, question):
    """
    Medical safety + accuracy validator.
    """
    prompt = f"""
    You are a medical safety and accuracy validation agent.
    Review the following answer for correctness, safety, and clarity.

    User question:
    {question}

    Initial answer:
    {final_answer}

    Your task:
    - Fix any medical inaccuracies.
    - Improve clarity.
    - Ensure safety warnings when needed.
    - Ensure the answer is aligned with evidence-based medical information.

    Produce the corrected, improved final answer.
    """

    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content

from openai import OpenAI
from backend.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def classification_agent(text: str) -> bool:
    """
    GPT Agent that determines if a document is medical.
    Returns True if medical, False otherwise.
    """

    if text == "IMAGE_ONLY_PDF":
        return False   # reject scanned unless OCR later


    prompt = f"""
You are a MEDICAL DOCUMENT CLASSIFICATION AGENT.

Your task is to decide whether the document is medical or non-medical.

A document is **MEDICAL** if it belongs to ANY of these categories:
- Medical research papers
- Scientific medical documents
- Clinical case reports
- Patient medical records
- Diagnostic summaries
- Mental health reports
- Medical journals or academic publications
- Public health research
- Clinical trial documents
- Biomedical research
- Physician evaluations or consultant reports

A document is **NON-MEDICAL** if it is:
- A lease agreement
- Real estate document
- Business or finance PDF
- Legal contract
- School/college assignment
- Marketing or general-purpose document
- Anything unrelated to health, medicine, biology, or clinical care

VERY IMPORTANT:
If the document contains **any significant medical keywords**, such as:
- diagnosis
- treatment
- patient
- symptoms
- clinical
- research
- disease
- medical history
- evaluation
- health
- physician
- hospital
- trial
- study
- imaging
- pathology
- cardiology
- neurology
- oncology
- surgery
- report
Then classify it as **MEDICAL**.

ONLY classify as non-medical if the document is clearly unrelated to medicine.

Document text:
{text[:5000]}

Respond with exactly ONE word:
medical
non-medical
"""




    out = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    result = out.choices[0].message.content.lower().strip()
    return result == "medical"

