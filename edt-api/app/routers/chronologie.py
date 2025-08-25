from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import JSONResponse, StreamingResponse
from ..lib.paths import get_data_dir
from app.lib.convertCourses import cours_to_chronologie
from datetime import datetime
from ..config import settings
from pathlib import Path
import os
import json
from typing import Optional, List
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm, cm
import zipfile

router = APIRouter(prefix="/chronologie", tags=["chronologie"])

DATA_COURS_DIR = get_data_dir() / f"cours/"


@router.get("/")
async def get_chronologie(
    professeur: Optional[str] = Query(None),
    semestre: Optional[str] = Query(None),
    matiere: Optional[str] = Query(None)
):
    tabGroupes = get_groupes_semestres()
    # Récupère les données (remplace par ton vrai code)

    # je veux récupérer le nom de l'intervenant en recherchant la clé dans le fichier contraintes.json
    data_globale_path = get_data_dir() / "contraintes.json"
    with open(data_globale_path, "r", encoding="utf-8") as f:
        data_globale = json.load(f)
    intervenants = data_globale

    cours_list = []
    if not DATA_COURS_DIR.exists():
        raise HTTPException(status_code=404, detail="Dossier data-GEA/cours introuvable")

    for file_name in os.listdir(DATA_COURS_DIR):
        if file_name.endswith(".json"):
            file_path = DATA_COURS_DIR / file_name
            with open(file_path, "r", encoding="utf-8") as f:
                ## extraire le numéro de semaine du nom de fichier
                week_number = file_name.split("_")[1].split(".")[0]
                data = json.load(f)
                if isinstance(data, list):
                    cours_items = data
                else:
                    cours_items = data.get("cours", [])
                for cours in cours_items:
                    # Filtrage selon les critères
                    if professeur and cours.get("professor") != professeur:
                        continue
                    if semestre and cours.get("semester") != semestre:
                        continue
                    if matiere and cours.get("matiere") != matiere:
                        continue
                    if cours.get("date") and cours.get("creneau"):
                        cours_list.append(cours_to_chronologie(cours, week_number, tabGroupes, intervenants))

    # Tri par date puis créneau
    cours_list.sort(key=lambda x: (
        datetime.strptime(x["date"] + " " + x["heure"], "%d/%m/%Y %H:%M")
    ))

    return JSONResponse(content=cours_list)

@router.get("/pdf")
async def get_chronologie_pdf(professeur: str = Query(...)):
    tabGroupes = get_groupes_semestres()
    data_globale_path = get_data_dir() / "contraintes.json"
    with open(data_globale_path, "r", encoding="utf-8") as f:
        intervenants = json.load(f)
    pdf_buffer = generate_prof_pdf(professeur, tabGroupes, intervenants)
    if not pdf_buffer:
        raise HTTPException(status_code=404, detail="Aucun cours trouvé pour ce professeur")
    return Response(pdf_buffer.read(), media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=service_chronologique.pdf"
    })
    # tabGroupes = get_groupes_semestres()
    # # Récupère les données (remplace par ton vrai code)
    #
    # # je veux récupérer le nom de l'intervenant en recherchant la clé dans le fichier contraintes.json
    # data_globale_path = get_data_dir() / "contraintes.json"
    # with open(data_globale_path, "r", encoding="utf-8") as f:
    #     data_globale = json.load(f)
    # intervenants = data_globale
    # name = intervenants.get(professeur, {}).get("name", professeur)
    # if not name:
    #     raise HTTPException(status_code=404, detail="Intervenant non trouvé")
    #
    # cours_list = []
    # if not DATA_COURS_DIR.exists():
    #     raise HTTPException(status_code=404, detail="Dossier data-GEA/cours introuvable")
    #
    # for file_name in os.listdir(DATA_COURS_DIR):
    #     if file_name.endswith(".json"):
    #         file_path = DATA_COURS_DIR / file_name
    #         with open(file_path, "r", encoding="utf-8") as f:
    #             ## extraire le numéro de semaine du nom de fichier
    #             week_number = file_name.split("_")[1].split(".")[0]
    #             data = json.load(f)
    #             if isinstance(data, list):
    #                 cours_items = data
    #             else:
    #                 cours_items = data.get("cours", [])
    #             for cours in cours_items:
    #                 # Filtrage selon les critères
    #                 if professeur and cours.get("professor") != professeur:
    #                     continue
    #                 if cours.get("date") and cours.get("creneau"):
    #                     cours_list.append(cours_to_chronologie(cours, week_number, tabGroupes, intervenants))
    #
    # # Tri par date puis créneau
    # cours_list.sort(key=lambda x: (
    #     datetime.strptime(x["date"] + " " + x["heure"], "%d/%m/%Y %H:%M")
    # ))
    #
    # buffer = BytesIO()
    # doc = SimpleDocTemplate(
    #     buffer,
    #     pagesize=A4,
    #     leftMargin=2 * cm,
    #     rightMargin=2 * cm
    # )
    # styles = getSampleStyleSheet()
    # elements = []
    #
    # # Largeur du tableau : largeur de la page - marges
    # table_width = A4[0] - 4 * cm
    # col_count = 8
    # col_width = table_width / col_count
    # col_widths = [col_width] * col_count
    #
    # # Titre
    # elements.append(Paragraph(settings.titre_pdf, styles['Title']))
    # elements.append(Paragraph(name, styles['Title']))
    # elements.append(Spacer(1, 12))
    #
    # # Tableau
    # data = [["Date", "Jour", "Heure début", "Heure fin", "Cours", "Semestre", "Salle", "Groupe"]]
    # for c in cours_list:
    #     data.append([c["date"],  c['jour'], c["heure"], c["heureFin"], c["matiere"], c["semester"], c.get("salle", ""), c.get("groupe", "")])
    #
    # table = Table(data, colWidths=col_widths, repeatRows=1)
    # table.setStyle(TableStyle([
    #     ("BACKGROUND", (0,0), (-1,0), colors.lightblue),
    #     ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    #     ("GRID", (0,0), (-1,-1), 1, colors.black),
    #     ("ALIGN", (0,0), (-1,-1), "CENTER"),
    #     ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    # ]))
    # elements.append(table)
    #
    # # Pagination
    # def add_page_number(canvas, doc):
    #     page_num = canvas.getPageNumber()
    #     text = f"Page {page_num}"
    #     canvas.drawRightString(200 * mm, 15 * mm, text)
    #
    # doc.build(elements, onLaterPages=add_page_number, onFirstPage=add_page_number)
    # buffer.seek(0)
    #
    # return Response(buffer.read(), media_type="application/pdf", headers={
    #     "Content-Disposition": "attachment; filename=service_chronologique.pdf"
    # })

def get_groupes_semestres():
    data_globale_path = get_data_dir() / "data_globale.json"
    with open(data_globale_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    semesters = data.get("semesters", {})
    groupes_semestre = {}
    for semestre, infos in semesters.items():
        groupes_semestre[semestre] = {}
        # TP
        groupes_tp = infos.get("groupesTp", {})
        groupes_semestre[semestre]["TP"] = {}
        for idx, val in groupes_tp.items():
            groupes_semestre[semestre]["TP"][int(idx)] = val
        # TD
        groupes_td = infos.get("groupesTd", {})
        groupes_semestre[semestre]["TD"] = {}
        if isinstance(groupes_td, dict):
            for idx, val in groupes_td.items():
                groupes_semestre[semestre]["TD"][int(idx)] = val
        elif isinstance(groupes_td, list):
            for i, val in enumerate(groupes_td, 1):
                groupes_semestre[semestre]["TD"][i] = val
    return groupes_semestre

def generate_prof_pdf(professeur, tabGroupes, intervenants):
    name = intervenants.get(professeur, {}).get("name", professeur)
    cours_list = []
    if not DATA_COURS_DIR.exists():
        return None
    for file_name in os.listdir(DATA_COURS_DIR):
        if file_name.endswith(".json"):
            file_path = DATA_COURS_DIR / file_name
            with open(file_path, "r", encoding="utf-8") as f:
                week_number = file_name.split("_")[1].split(".")[0]
                data = json.load(f)
                cours_items = data if isinstance(data, list) else data.get("cours", [])
                for cours in cours_items:
                    if cours.get("professor") != professeur:
                        continue
                    if cours.get("date") and cours.get("creneau"):
                        cours_list.append(cours_to_chronologie(cours, week_number, tabGroupes, intervenants))
    if not cours_list:
        return None
    cours_list.sort(key=lambda x: (
        datetime.strptime(x["date"] + " " + x["heure"], "%d/%m/%Y %H:%M")
    ))
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm)
    styles = getSampleStyleSheet()
    elements = []
    table_width = A4[0] - 4 * cm
    col_count = 8
    col_width = table_width / col_count
    col_widths = [col_width] * col_count
    elements.append(Paragraph(settings.titre_pdf, styles['Title']))
    elements.append(Paragraph(name, styles['Title']))
    elements.append(Spacer(1, 12))
    data = [["Date", "Jour", "Heure début", "Heure fin", "Cours", "Semestre", "Salle", "Groupe"]]
    for c in cours_list:
        data.append([c["date"],  c['jour'], c["heure"], c["heureFin"], c["matiere"], c["semester"], c.get("salle", ""), c.get("groupe", "")])
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))
    elements.append(table)
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(200 * mm, 15 * mm, text)
    doc.build(elements, onLaterPages=add_page_number, onFirstPage=add_page_number)
    buffer.seek(0)
    return buffer

@router.get("/all-pdf")
async def get_all_chronologie_pdf():
    tabGroupes = get_groupes_semestres()
    data_globale_path = get_data_dir() / "contraintes.json"
    with open(data_globale_path, "r", encoding="utf-8") as f:
        intervenants = json.load(f)
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for prof in intervenants.keys():
            pdf_buffer = generate_prof_pdf(prof, tabGroupes, intervenants)
            if pdf_buffer:
                zipf.writestr(f"{prof}.pdf", pdf_buffer.getvalue())
    zip_buffer.seek(0)
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={
        "Content-Disposition": "attachment; filename=chronologies_profs.zip"
    })