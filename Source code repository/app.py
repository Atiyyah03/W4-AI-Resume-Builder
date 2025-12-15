
import gradio as gr
from transformers import pipeline
from fpdf import FPDF

generator = pipeline("text-generation", model="tiiuae/falcon-7b-instruct")

skills_list = [
    "Python", "Java", "Machine Learning", "AI", "SQL", "Data Analysis", "Leadership",
    "Communication", "Cloud Computing", "DevOps", "Project Management", "C++", "JavaScript",
    "HTML", "CSS", "Tableau", "Power BI", "Excel", "Business Analysis", "Problem Solving"
]

def generate_resume(job_title, skills, experience, education, job_description):
    prompt = (
        f"Write a detailed, professional resume summary for a {job_title}. "
        f"Highlight achievements, years of experience, and key skills ({skills}). "
        f"Include leadership and technical expertise from this experience: {experience}. "
        f"Add education details: {education}. "
        f"Make it formal, ATS-friendly, and at least 4 sentences long."
    )

    result = generator(prompt, max_length=250, temperature=0.7, do_sample=True)
    summary = result[0]['generated_text'].replace(prompt, "").strip()

    found_skills = [skill for skill in skills_list if skill.lower() in (skills + " " + experience).lower()]

    ats_keywords = []
    if job_description.strip():
        for skill in skills_list:
            if skill.lower() in job_description.lower() and skill not in found_skills:
                ats_keywords.append(skill)
    else:
        ats_keywords = [skill for skill in skills_list if skill not in found_skills]

    if not ats_keywords:
        ats_keywords = ["No additional keywords found"]

    return summary, ", ".join(found_skills), ", ".join(ats_keywords)

def export_pdf(summary, skills, ats_keywords, experience, education):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="AI Generated Resume", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Summary:
{summary}

Skills:
{skills}

ATS Keywords:
{ats_keywords}

Experience:
{experience}

Education:
{education}")
    file_path = "/tmp/resume.pdf"
    pdf.output(file_path)
    return file_path

with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align:center;'>AI Resume Builder</h1>")
    gr.Markdown("Generate a professional, ATS-friendly resume summary with skills and education.")

    with gr.Row():
        job_title = gr.Textbox(label="Job Title")
        skills = gr.Textbox(label="Skills (comma-separated)")
    experience = gr.Textbox(label="Experience Summary")
    education = gr.Textbox(label="Education Details")
    job_description = gr.Textbox(label="Target Job Description")

    summary_output = gr.Textbox(label="Generated Resume Summary", lines=6)
    skills_output = gr.Textbox(label="Extracted Skills")
    ats_output = gr.Textbox(label="ATS Keyword Suggestions")

    btn_generate = gr.Button("Generate Resume")
    btn_generate.click(generate_resume, inputs=[job_title, skills, experience, education, job_description],
                       outputs=[summary_output, skills_output, ats_output])

    btn_pdf = gr.Button("Export Full Resume to PDF")
    btn_pdf.click(export_pdf, inputs=[summary_output, skills_output, ats_output, experience, education], outputs=gr.File())

demo.launch()
