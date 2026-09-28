"""
sample.py — seeds the hosted demo with one document.

The demo is useless if the first thing it asks for is a PDF the visitor does
not have to hand, so this builds a short fictional handbook at startup and
indexes it. Each page carries distinct, checkable facts, which is what makes
the page-level citations worth looking at.

Only runs when DEMO_SAMPLE=1.
"""

import fitz  # PyMuPDF

FILENAME = "northwind-handbook-sample.pdf"

PAGES = [
    ("Northwind Corp - Employee Handbook\n\n1. Working Hours\n\n"
     "Core hours are 10:00 to 16:00, within a flexible working day that may "
     "start no earlier than 07:00 and end no later than 20:00.\n\n"
     "Employees may work remotely up to three days per week. Fully remote "
     "arrangements require director approval and are reviewed every six "
     "months.\n\n"
     "Overtime is not expected. Where it happens, it is compensated as time "
     "off in lieu at a rate of 1.5 hours per hour worked, to be taken within "
     "60 days."),

    ("2. Leave\n\n"
     "Employees accrue 24 days of paid annual leave per calendar year, rising "
     "to 27 days after four years of continuous service.\n\n"
     "Up to 5 unused days may be carried into the following year and must be "
     "used before 31 March, after which they lapse.\n\n"
     "Sick leave is capped at 10 paid days per year. A doctor's note is "
     "required from the fourth consecutive day of absence.\n\n"
     "Parental leave is 18 weeks at full pay for the primary carer and 6 weeks "
     "at full pay for the secondary carer."),

    ("3. Equipment and Expenses\n\n"
     "Each employee receives a laptop refreshed every three years, and a "
     "one-time home-office allowance of PKR 75,000.\n\n"
     "Expenses under PKR 20,000 are approved by a line manager. Anything above "
     "that requires finance approval before the spend, not after.\n\n"
     "Claims must be submitted within 45 days of the expense date. Claims "
     "submitted later are paid only at the discretion of the finance lead.\n\n"
     "Travel is booked through the company portal. Economy class is standard "
     "for flights under six hours."),

    ("4. Security and Data Handling\n\n"
     "Multi-factor authentication is mandatory on all company accounts. "
     "Hardware keys are issued to anyone with production access.\n\n"
     "Customer data may not be copied to personal devices or to any service "
     "outside the approved vendor list.\n\n"
     "Suspected security incidents must be reported within one hour of "
     "discovery to the security lead, regardless of the time of day.\n\n"
     "Laptops are full-disk encrypted. A lost device must be reported "
     "immediately so it can be remotely wiped."),
]


def build_pdf() -> bytes:
    doc = fitz.open()
    for body in PAGES:
        page = doc.new_page()
        page.insert_textbox(
            fitz.Rect(64, 72, 531, 760), body,
            fontsize=11.5, fontname="helv", lineheight=1.45,
        )
    data = doc.tobytes()
    doc.close()
    return data


def preload(store) -> int:
    """Index the sample handbook. Returns the number of chunks added."""
    return store.add_document(build_pdf(), FILENAME, "pdf")
