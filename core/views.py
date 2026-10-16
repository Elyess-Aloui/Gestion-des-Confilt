import os
import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .db_service import (
    users_col, instituts_col, salles_col, matieres_col, enseignants_col,
    classes_col, emplois_du_temps_col, emplois_du_temps_enseignants_col, absence_claims_col,
    resolve_institut, get_enseignants_for_institut, get_salles_for_institut, get_classes_for_institut,
    get_all_matieres, get_classe_timetable, save_classe_timetable,
    get_populated_classe_timetable, get_teacher_timetable, save_teacher_timetable,
    get_populated_teacher_timetable, get_enseignant_timetable
)
from .forms import (
    LoginForm, SignupForm, InstitutForm, SalleForm, SalleBreakdownForm,
    MatiereForm, EnseignantForm, AbsenceClaimForm, ClasseForm
)
from .models import GOUVERNORATS, NIVEAUX, SALLE_TYPES, MATIERES_PAR_DEFAUT, JOURS_SEMAINE, CRENEAUX_HORAIRES

def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, "Veuillez vous connecter pour accéder à cette page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# ---------------------------- AUTH VIEWS ---------------------------- #

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            existing = users_col().find_one({'username': username})
            if existing:
                messages.error(request, "Ce nom d'utilisateur existe déjà.")
            else:
                user_id = users_col().insert_one({
                    'username': username,
                    'email': email,
                    'password_hash': make_password(password),
                })
                request.session['user_id'] = user_id
                request.session['username'] = username
                messages.success(request, f"Bienvenue, {username} ! Inscription réussie.")
                return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'auth/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = users_col().find_one({'username': username})
            if user and check_password(password, user['password_hash']):
                request.session['user_id'] = user['_id']
                request.session['username'] = user['username']
                messages.success(request, f"Ravi de vous revoir, {user['username']} !")
                return redirect('dashboard')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    request.session.flush()
    messages.info(request, "Vous êtes déconnecté.")
    return redirect('login')

# ---------------------------- DASHBOARD VIEW ---------------------------- #

@login_required_custom
def dashboard_view(request):
    instituts_count = len(instituts_col().find())
    matieres_count = len(matieres_col().find())
    enseignants_count = len(enseignants_col().find())
    salles_count = len(salles_col().find())
    classes_count = len(classes_col().find())
    
    context = {
        'schools_count': instituts_count,
        'matieres_count': matieres_count,
        'teachers_count': enseignants_count,
        'salles_count': salles_count,
        'classes_count': classes_count,
    }
    return render(request, 'dashboard.html', context)

# ---------------------------- 1. GESTION DES INSTITUTS ---------------------------- #

@login_required_custom
def school_list_view(request):
    instituts = instituts_col().find()
    gov_dict = dict(GOUVERNORATS)
    for inst in instituts:
        inst['region_display'] = gov_dict.get(inst.get('region'), inst.get('region'))
    return render(request, 'schools/list.html', {'schools': instituts})

@login_required_custom
def school_add_view(request):
    if request.method == 'POST':
        form = InstitutForm(request.POST)
        if form.is_valid():
            instituts_col().insert_one({
                'nom': form.cleaned_data['nom'],
                'region': form.cleaned_data['region'],
                'ville': form.cleaned_data['ville'],
            })
            messages.success(request, "L'institut a été ajouté avec succès !")
            return redirect('school_list')
    else:
        form = InstitutForm()
    return render(request, 'schools/add.html', {'form': form})

# ---------------------------- 2. GESTION DES ENSEIGNANTS ---------------------------- #

@login_required_custom
def teacher_school_select_view(request):
    instituts = instituts_col().find()
    gov_dict = dict(GOUVERNORATS)
    for inst in instituts:
        inst['region_display'] = gov_dict.get(inst.get('region'), inst.get('region'))
    return render(request, 'teachers/select_school.html', {'schools': instituts})

@login_required_custom
def teacher_list_view(request, school_id):
    institut = resolve_institut(school_id)
    if not institut:
        messages.error(request, "Institut non trouvé.")
        return redirect('teacher_school_select')

    enseignants = get_enseignants_for_institut(school_id)
    claim_form = AbsenceClaimForm()
    context = {
        'school': institut,
        'teachers': enseignants,
        'claim_form': claim_form,
    }
    return render(request, 'teachers/list.html', context)

@login_required_custom
def teacher_add_view(request, school_id):
    institut = resolve_institut(school_id)
    if not institut:
        messages.error(request, "Institut non trouvé.")
        return redirect('teacher_school_select')

    if request.method == 'POST':
        form = EnseignantForm(request.POST)
        if form.is_valid():
            enseignants_col().insert_one({
                'institut_id': school_id,
                'nom': form.cleaned_data['nom'],
                'niveaux': form.cleaned_data['niveaux'],
                'volume_horaire': form.cleaned_data['volume_horaire'],
                'schedule_text': "Non renseigné",
            })
            messages.success(request, f"L'enseignant {form.cleaned_data['nom']} a été ajouté !")
            return redirect('teacher_list', school_id=school_id)
    else:
        form = EnseignantForm()
    return render(request, 'teachers/add.html', {'form': form, 'school': institut})

@login_required_custom
def teacher_timetable_view(request, teacher_id):
    enseignant = enseignants_col().find_one({'_id': teacher_id})
    if not enseignant:
        messages.error(request, "Enseignant introuvable.")
        return redirect('teacher_school_select')

    school_id = enseignant['institut_id']
    institut = resolve_institut(school_id)
    classes_list = get_classes_for_institut(school_id)
    rooms = get_salles_for_institut(school_id)
    matieres = get_all_matieres()

    if request.method == 'POST':
        seances = {}
        for jour_key, _ in JOURS_SEMAINE:
            seances[jour_key] = {}
            for slot_idx in range(len(CRENEAUX_HORAIRES)):
                c_id = request.POST.get(f"seance_{jour_key}_{slot_idx}_classe", "").strip()
                m_id = request.POST.get(f"seance_{jour_key}_{slot_idx}_matiere", "").strip()
                s_id = request.POST.get(f"seance_{jour_key}_{slot_idx}_salle", "").strip()
                seances[jour_key][str(slot_idx)] = {
                    'classe_id': c_id,
                    'matiere_id': m_id,
                    'salle_id': s_id,
                }
        commentaire = request.POST.get('commentaire', '').strip()
        save_teacher_timetable(teacher_id, seances, commentaire)
        messages.success(request, f"Emploi du temps enregistré avec succès pour {enseignant['nom']} !")
        return redirect('teacher_timetable', teacher_id=teacher_id)

    pop_timetable = get_populated_teacher_timetable(teacher_id, school_id)
    raw_seances = pop_timetable.get('seances', {})

    grid_rows = []
    for slot_idx, (slot_label, _) in enumerate(CRENEAUX_HORAIRES):
        row = {
            'slot_idx': slot_idx,
            'slot_label': slot_label,
            'days': []
        }
        for jour_key, jour_label in JOURS_SEMAINE:
            day_slot_data = raw_seances.get(jour_key, {}).get(str(slot_idx), {})
            row['days'].append({
                'jour_key': jour_key,
                'jour_label': jour_label,
                'classe_id': day_slot_data.get('classe_id', ''),
                'matiere_id': day_slot_data.get('matiere_id', ''),
                'salle_id': day_slot_data.get('salle_id', ''),
                'classe_nom': day_slot_data.get('classe_nom', ''),
                'matiere_nom': day_slot_data.get('matiere_nom', ''),
                'salle_numero': day_slot_data.get('salle_numero', ''),
                'has_course': bool(day_slot_data.get('classe_id') or day_slot_data.get('matiere_id') or day_slot_data.get('salle_id'))
            })
        grid_rows.append(row)

    context = {
        'teacher': enseignant,
        'school': institut,
        'classes': classes_list,
        'rooms': rooms,
        'matieres': matieres,
        'jours': JOURS_SEMAINE,
        'creneaux': CRENEAUX_HORAIRES,
        'grid_rows': grid_rows,
        'commentaire': pop_timetable.get('commentaire', ''),
        'date_modification': pop_timetable.get('date_modification', ''),
    }
    return render(request, 'teachers/timetable.html', context)

@login_required_custom
def download_teacher_timetable_pdf_view(request, teacher_id):
    enseignant = enseignants_col().find_one({'_id': teacher_id})
    if not enseignant:
        messages.error(request, "Enseignant introuvable.")
        return redirect('teacher_school_select')

    school_id = enseignant['institut_id']
    institut = resolve_institut(school_id)
    institut_nom = institut['nom'] if institut else "Institut"
    pop_timetable = get_populated_teacher_timetable(teacher_id, school_id)
    raw_seances = pop_timetable.get('seances', {})

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor("#1e293b"), alignment=1, spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#64748b"), alignment=1, spaceAfter=15
    )
    cell_style = ParagraphStyle(
        'CellStyle', parent=styles['Normal'], fontSize=7.5, leading=10, alignment=1
    )
    header_style = ParagraphStyle(
        'HeaderStyle', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.white, fontName="Helvetica-Bold", alignment=1
    )

    elements.append(Paragraph(f"EMPLOI DU TEMPS - {enseignant['nom'].upper()}", title_style))
    elements.append(Paragraph(f"Établissement : {institut_nom} | Planning individuel hebdomadaire", subtitle_style))

    if pop_timetable.get('commentaire'):
        elements.append(Paragraph(f"<b>Remarques :</b> {pop_timetable['commentaire']}", styles['Normal']))
        elements.append(Spacer(1, 10))

    table_data = []
    header_row = [Paragraph("<b>Jour / Heure</b>", header_style)]
    for slot_label, _ in CRENEAUX_HORAIRES:
        header_row.append(Paragraph(f"<b>{slot_label}</b>", header_style))
    table_data.append(header_row)

    for jour_key, jour_label in JOURS_SEMAINE:
        row = [Paragraph(f"<b>{jour_label}</b>", ParagraphStyle('DayCol', parent=styles['Normal'], fontSize=8, leading=11, fontName="Helvetica-Bold", alignment=1))]
        for slot_idx in range(len(CRENEAUX_HORAIRES)):
            s = raw_seances.get(jour_key, {}).get(str(slot_idx), {})
            c_nom = s.get('classe_nom', '')
            m_nom = s.get('matiere_nom', '')
            s_num = s.get('salle_numero', '')

            if c_nom or m_nom or s_num:
                parts = []
                if c_nom: parts.append(f"<b>{c_nom}</b>")
                if m_nom: parts.append(f"<font color='#4f46e5'>{m_nom}</font>")
                if s_num: parts.append(f"<font color='#059669'>Salle: {s_num}</font>")
                row.append(Paragraph("<br/>".join(parts), cell_style))
            else:
                row.append(Paragraph("<font color='#9ca3af'>-</font>", cell_style))
        table_data.append(row)

    col_widths = [70, 120, 120, 120, 120]
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4f46e5")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    elements.append(t)
    elements.append(Spacer(1, 15))
    footer_text = f"Document officiel généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Italic'], fontSize=8, textColor=colors.gray, alignment=1)))

    doc.build(elements)
    buffer.seek(0)

    filename = f"emploi_du_temps_enseignant_{enseignant['nom'].replace(' ', '_')}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required_custom
def absence_claim_add_view(request, teacher_id):
    enseignant = enseignants_col().find_one({'_id': teacher_id})
    if not enseignant:
        messages.error(request, "Enseignant non trouvé.")
        return redirect('teacher_school_select')

    school_id = enseignant['institut_id']
    if request.method == 'POST':
        form = AbsenceClaimForm(request.POST)
        if form.is_valid():
            absence_claims_col().insert_one({
                'teacher_id': teacher_id,
                'institut_id': school_id,
                'teacher_name': enseignant['nom'],
                'reason': form.cleaned_data['reason'],
                'date_start': form.cleaned_data['date_start'],
                'date_end': form.cleaned_data['date_end'],
                'status': 'En attente',
            })
            messages.success(request, f"Réclamation d'absence enregistrée pour {enseignant['nom']} !")
    return redirect('teacher_list', school_id=school_id)

# ---------------------------- 3. GESTION DES SALLES ---------------------------- #

@login_required_custom
def room_school_select_view(request):
    instituts = instituts_col().find()
    gov_dict = dict(GOUVERNORATS)
    for inst in instituts:
        inst['region_display'] = gov_dict.get(inst.get('region'), inst.get('region'))
    return render(request, 'rooms/select_school.html', {'schools': instituts})

@login_required_custom
def room_list_view(request, school_id):
    institut = resolve_institut(school_id)
    if not institut:
        messages.error(request, "Institut non trouvé.")
        return redirect('room_school_select')

    salles = get_salles_for_institut(school_id)
    breakdown_form = SalleBreakdownForm()
    context = {
        'school': institut,
        'rooms': salles,
        'breakdown_form': breakdown_form
    }
    return render(request, 'rooms/list.html', context)

@login_required_custom
def room_add_view(request, school_id):
    institut = resolve_institut(school_id)
    if not institut:
        messages.error(request, "Institut non trouvé.")
        return redirect('room_school_select')

    if request.method == 'POST':
        form = SalleForm(request.POST)
        if form.is_valid():
            salles_col().insert_one({
                'institut_id': school_id,
                'numero': form.cleaned_data['numero'],
                'type': form.cleaned_data['type'],
                'capacite': form.cleaned_data['capacite'],
                'is_broken': False,
                'broken_duration': '',
            })
            messages.success(request, "La salle a été ajoutée avec succès !")
            return redirect('room_list', school_id=school_id)
    else:
        form = SalleForm()
    return render(request, 'rooms/add.html', {'form': form, 'school': institut})

@login_required_custom
def room_mark_broken_view(request, room_id):
    salle = salles_col().find_one({'_id': room_id})
    if not salle:
        messages.error(request, "Salle non trouvée.")
        return redirect('room_school_select')

    school_id = salle['institut_id']
    if request.method == 'POST':
        form = SalleBreakdownForm(request.POST)
        if form.is_valid():
            duration = form.cleaned_data['broken_duration']
            is_currently_broken = salle.get('is_broken', False)
            new_status = not is_currently_broken if not duration else True
            
            salles_col().update_one(
                {'_id': room_id},
                {
                    'is_broken': new_status,
                    'broken_duration': duration if new_status else '',
                }
            )
            status_text = f"marquée EN PANNE (durée: {duration})" if new_status else "remise en service"
            messages.warning(request, f"La salle {salle['numero']} a été {status_text}.")

    return redirect('room_list', school_id=school_id)

# ---------------------------- 4. GESTION DES CLASSES ---------------------------- #

@login_required_custom
def class_school_select_view(request):
    instituts = instituts_col().find()
    gov_dict = dict(GOUVERNORATS)
    for inst in instituts:
        inst['region_display'] = gov_dict.get(inst.get('region'), inst.get('region'))
    return render(request, 'classes/select_school.html', {'schools': instituts})

@login_required_custom
def class_list_view(request, school_id):
    institut = resolve_institut(school_id)
    if not institut:
        messages.error(request, "Institut non trouvé.")
        return redirect('class_school_select')

    classes_list = get_classes_for_institut(school_id)
    context = {
        'school': institut,
        'classes': classes_list,
    }
    return render(request, 'classes/list.html', context)

@login_required_custom
def class_add_view(request, school_id):
    institut = resolve_institut(school_id)
    if not institut:
        messages.error(request, "Institut non trouvé.")
        return redirect('class_school_select')

    if request.method == 'POST':
        form = ClasseForm(request.POST)
        if form.is_valid():
            classes_col().insert_one({
                'institut_id': school_id,
                'niveau': int(form.cleaned_data['niveau']),
                'nom': form.cleaned_data['nom'],
            })
            messages.success(request, f"La classe Niveau {form.cleaned_data['niveau']} - {form.cleaned_data['nom']} a été créée !")
            return redirect('class_list', school_id=school_id)
    else:
        form = ClasseForm()
    return render(request, 'classes/add.html', {'form': form, 'school': institut})

@login_required_custom
def class_timetable_view(request, class_id):
    classe = classes_col().find_one({'_id': class_id})
    if not classe:
        messages.error(request, "Classe introuvable.")
        return redirect('class_school_select')

    school_id = classe['institut_id']
    institut = resolve_institut(school_id)
    teachers = get_enseignants_for_institut(school_id)
    rooms = get_salles_for_institut(school_id)
    matieres = get_all_matieres()

    if request.method == 'POST':
        seances = {}
        for jour_key, _ in JOURS_SEMAINE:
            seances[jour_key] = {}
            for slot_idx in range(len(CRENEAUX_HORAIRES)):
                m_id = request.POST.get(f"seance_{jour_key}_{slot_idx}_matiere", "").strip()
                t_id = request.POST.get(f"seance_{jour_key}_{slot_idx}_enseignant", "").strip()
                s_id = request.POST.get(f"seance_{jour_key}_{slot_idx}_salle", "").strip()
                seances[jour_key][str(slot_idx)] = {
                    'matiere_id': m_id,
                    'enseignant_id': t_id,
                    'salle_id': s_id,
                }
        commentaire = request.POST.get('commentaire', '').strip()
        save_classe_timetable(class_id, seances, commentaire)
        messages.success(request, f"Emploi du temps enregistré pour Niveau {classe['niveau']} - {classe['nom']} !")
        return redirect('class_timetable', class_id=class_id)

    pop_timetable = get_populated_classe_timetable(class_id)
    raw_seances = pop_timetable.get('seances', {})

    # Grille ligne par créneau avec liste des jours
    grid_rows = []
    for slot_idx, (slot_label, _) in enumerate(CRENEAUX_HORAIRES):
        row = {
            'slot_idx': slot_idx,
            'slot_label': slot_label,
            'days': []
        }
        for jour_key, jour_label in JOURS_SEMAINE:
            day_slot_data = raw_seances.get(jour_key, {}).get(str(slot_idx), {})
            row['days'].append({
                'jour_key': jour_key,
                'jour_label': jour_label,
                'matiere_id': day_slot_data.get('matiere_id', ''),
                'enseignant_id': day_slot_data.get('enseignant_id', ''),
                'salle_id': day_slot_data.get('salle_id', ''),
                # --- FIX : ces 3 champs manquaient, d'ou "Matiere non definie" / "Non assigne" ---
                'matiere_nom': day_slot_data.get('matiere_nom', ''),
                'enseignant_nom': day_slot_data.get('enseignant_nom', ''),
                'salle_numero': day_slot_data.get('salle_numero', ''),
            })
        grid_rows.append(row)

    context = {
        'classe': classe,
        'school': institut,
        'teachers': teachers,
        'rooms': rooms,
        'matieres': matieres,
        'jours': JOURS_SEMAINE,
        'creneaux': CRENEAUX_HORAIRES,
        'grid_rows': grid_rows,
        'commentaire': pop_timetable.get('commentaire', ''),
        'date_modification': pop_timetable.get('date_modification', ''),
    }
    return render(request, 'classes/timetable.html', context)

@login_required_custom
def download_class_timetable_pdf_view(request, class_id):
    classe = classes_col().find_one({'_id': class_id})
    if not classe:
        messages.error(request, "Classe introuvable.")
        return redirect('class_school_select')

    institut = resolve_institut(classe['institut_id'])
    institut_nom = institut['nom'] if institut else "Institut"

    pop_timetable = get_populated_classe_timetable(class_id)
    raw_seances = pop_timetable.get('seances', {})

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor("#1e293b"), alignment=1, spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#64748b"), alignment=1, spaceAfter=15
    )
    cell_style = ParagraphStyle(
        'CellStyle', parent=styles['Normal'], fontSize=7.5, leading=10, alignment=1
    )
    header_style = ParagraphStyle(
        'HeaderStyle', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.white, fontName="Helvetica-Bold", alignment=1
    )

    elements.append(Paragraph(f"EMPLOI DU TEMPS - NIVEAU {classe['niveau']} ({classe['nom'].upper()})", title_style))
    elements.append(Paragraph(f"Établissement : {institut_nom} | Année Scolaire en cours", subtitle_style))

    if pop_timetable.get('commentaire'):
        elements.append(Paragraph(f"<b>Remarques :</b> {pop_timetable['commentaire']}", styles['Normal']))
        elements.append(Spacer(1, 10))

    table_data = []
    header_row = [Paragraph("<b>Jour / Heure</b>", header_style)]
    for slot_label, _ in CRENEAUX_HORAIRES:
        header_row.append(Paragraph(f"<b>{slot_label}</b>", header_style))
    table_data.append(header_row)

    for jour_key, jour_label in JOURS_SEMAINE:
        row = [Paragraph(f"<b>{jour_label}</b>", ParagraphStyle('DayCol', parent=styles['Normal'], fontSize=8, leading=11, fontName="Helvetica-Bold", alignment=1))]
        for slot_idx in range(len(CRENEAUX_HORAIRES)):
            s = raw_seances.get(jour_key, {}).get(str(slot_idx), {})
            m_nom = s.get('matiere_nom', '')
            t_nom = s.get('enseignant_nom', '')
            s_num = s.get('salle_numero', '')

            if m_nom or t_nom or s_num:
                parts = []
                if m_nom: parts.append(f"<b>{m_nom}</b>")
                if t_nom: parts.append(f"<font color='#4f46e5'>{t_nom}</font>")
                if s_num: parts.append(f"<font color='#059669'>Salle: {s_num}</font>")
                row.append(Paragraph("<br/>".join(parts), cell_style))
            else:
                row.append(Paragraph("<font color='#9ca3af'>-</font>", cell_style))
        table_data.append(row)

    col_widths = [70, 120, 120, 120, 120]
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2563eb")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    elements.append(t)
    elements.append(Spacer(1, 15))
    footer_text = f"Document officiel généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Italic'], fontSize=8, textColor=colors.gray, alignment=1)))

    doc.build(elements)
    buffer.seek(0)

    filename = f"emploi_du_temps_niveau_{classe['niveau']}_{classe['nom']}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

# ---------------------------- REST API ENDPOINTS FOR FLUTTER ---------------------------- #

@csrf_exempt
@api_view(['POST'])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = users_col().find_one({'username': username})
    if user and check_password(password, user['password_hash']):
        return Response({'status': 'success', 'user_id': user['_id'], 'username': user['username']})
    return Response({'status': 'error', 'message': 'Identifiants invalides'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def api_signup(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    if users_col().find_one({'username': username}):
        return Response({'status': 'error', 'message': 'Utilisateur existant'}, status=status.HTTP_400_BAD_REQUEST)
    user_id = users_col().insert_one({
        'username': username,
        'email': email,
        'password_hash': make_password(password)
    })
    return Response({'status': 'success', 'user_id': user_id, 'username': username})

@csrf_exempt
@api_view(['GET', 'POST'])
def api_schools(request):
    if request.method == 'GET':
        instituts = instituts_col().find()
        return Response(instituts)
    elif request.method == 'POST':
        iid = instituts_col().insert_one({
            'nom': request.data.get('nom'),
            'region': request.data.get('region'),
            'ville': request.data.get('ville'),
        })
        return Response({'status': 'success', '_id': iid})

@csrf_exempt
@api_view(['GET', 'POST'])
def api_teachers(request, school_id):
    if request.method == 'GET':
        enseignants = get_enseignants_for_institut(school_id)
        return Response(enseignants)
    elif request.method == 'POST':
        eid = enseignants_col().insert_one({
            'institut_id': school_id,
            'nom': request.data.get('nom'),
            'niveaux': request.data.get('niveaux', 'Niveau 1, Niveau 2'),
            'volume_horaire': int(request.data.get('volume_horaire', 18)),
            'schedule_text': request.data.get('schedule_text', 'Non renseigné')
        })
        return Response({'status': 'success', '_id': eid})

@csrf_exempt
@api_view(['GET', 'POST'])
def api_rooms(request, school_id):
    if request.method == 'GET':
        salles = get_salles_for_institut(school_id)
        return Response(salles)
    elif request.method == 'POST':
        sid = salles_col().insert_one({
            'institut_id': school_id,
            'numero': request.data.get('numero'),
            'type': request.data.get('type', 'normale'),
            'capacite': int(request.data.get('capacite', 30)),
            'is_broken': False,
            'broken_duration': ''
        })
        return Response({'status': 'success', '_id': sid})

@csrf_exempt
@api_view(['GET', 'POST'])
def api_classes(request, school_id):
    if request.method == 'GET':
        classes_list = get_classes_for_institut(school_id)
        return Response(classes_list)
    elif request.method == 'POST':
        cid = classes_col().insert_one({
            'institut_id': school_id,
            'niveau': int(request.data.get('niveau', 1)),
            'nom': request.data.get('nom')
        })
        return Response({'status': 'success', '_id': cid})

@csrf_exempt
@api_view(['GET', 'POST'])
def api_teacher_timetable(request, teacher_id):
    enseignant = enseignants_col().find_one({'_id': teacher_id})
    if not enseignant:
        return Response({'status': 'error', 'message': 'Enseignant non trouvé'}, status=404)
    if request.method == 'GET':
        data = get_populated_teacher_timetable(teacher_id, enseignant['institut_id'])
        return Response(data)
    elif request.method == 'POST':
        seances = request.data.get('seances', {})
        commentaire = request.data.get('commentaire', '')
        save_teacher_timetable(teacher_id, seances, commentaire)
        return Response({'status': 'success'})

@csrf_exempt
@api_view(['POST'])
def api_update_teacher_schedule(request, teacher_id):
    schedule = request.data.get('schedule_text', '')
    enseignants_col().update_one({'_id': teacher_id}, {'schedule_text': schedule})
    return Response({'status': 'success'})

@csrf_exempt
@api_view(['POST'])
def api_claim_absence(request, teacher_id):
    enseignant = enseignants_col().find_one({'_id': teacher_id})
    if not enseignant:
        return Response({'status': 'error', 'message': 'Enseignant non trouvé'}, status=404)
    cid = absence_claims_col().insert_one({
        'teacher_id': teacher_id,
        'institut_id': enseignant['institut_id'],
        'teacher_name': enseignant['nom'],
        'reason': request.data.get('reason'),
        'date_start': request.data.get('date_start'),
        'date_end': request.data.get('date_end'),
        'status': 'En attente',
    })
    return Response({'status': 'success', '_id': cid})

@csrf_exempt
@api_view(['POST'])
def api_room_breakdown(request, room_id):
    duration = request.data.get('broken_duration', '')
    salle = salles_col().find_one({'_id': room_id})
    if not salle:
        return Response({'status': 'error', 'message': 'Salle non trouvée'}, status=404)
    is_broken = not salle.get('is_broken', False) if not duration else True
    salles_col().update_one({'_id': room_id}, {
        'is_broken': is_broken,
        'broken_duration': duration if is_broken else ''
    })
    return Response({'status': 'success', 'is_broken': is_broken, 'broken_duration': duration})

@csrf_exempt
@api_view(['GET', 'POST'])
def api_class_timetable(request, class_id):
    classe = classes_col().find_one({'_id': class_id})
    if not classe:
        return Response({'status': 'error', 'message': 'Classe introuvable'}, status=404)
    if request.method == 'GET':
        data = get_populated_classe_timetable(class_id)
        return Response(data)
    elif request.method == 'POST':
        seances = request.data.get('seances', {})
        commentaire = request.data.get('commentaire', '')
        save_classe_timetable(class_id, seances, commentaire)
        return Response({'status': 'success'})

@csrf_exempt
@api_view(['POST'])
def api_update_class_schedule(request, class_id):
    details = request.data.get('schedule_details', '')
    classes_col().update_one({'_id': class_id}, {'schedule_details': details})
    return Response({'status': 'success'})

@csrf_exempt
@api_view(['DELETE'])
def api_delete_school(request, school_id):
    instituts_col().delete_one({'_id': school_id})
    return Response({'status': 'success'})

@csrf_exempt
@api_view(['DELETE'])
def api_delete_teacher(request, teacher_id):
    enseignants_col().delete_one({'_id': teacher_id})
    return Response({'status': 'success'})

@csrf_exempt
@api_view(['DELETE'])
def api_delete_room(request, room_id):
    salles_col().delete_one({'_id': room_id})
    return Response({'status': 'success'})

@csrf_exempt
@api_view(['DELETE'])
def api_delete_class(request, class_id):
    classes_col().delete_one({'_id': class_id})
    return Response({'status': 'success'})

@csrf_exempt
@api_view(['GET', 'POST'])
def api_matieres(request):
    if request.method == 'GET':
        matieres = get_all_matieres()
        return Response(matieres)
    elif request.method == 'POST':
        niveaux = request.data.get('niveaux', [])
        if isinstance(niveaux, str):
            niveaux = [n.strip() for n in niveaux.split(',') if n.strip()]
        mid = matieres_col().insert_one({
            'nom': request.data.get('nom'),
            'niveaux': niveaux,
            'volume_horaire': int(request.data.get('volume_horaire', 4)),
        })
        return Response({'status': 'success', '_id': mid})

@csrf_exempt
@api_view(['PUT', 'DELETE'])
def api_matiere_detail(request, matiere_id):
    if request.method == 'DELETE':
        matieres_col().delete_one({'_id': matiere_id})
        return Response({'status': 'success'})
    elif request.method == 'PUT':
        niveaux = request.data.get('niveaux', [])
        if isinstance(niveaux, str):
            niveaux = [n.strip() for n in niveaux.split(',') if n.strip()]
        matieres_col().update_one({'_id': matiere_id}, {
            'nom': request.data.get('nom'),
            'niveaux': niveaux,
            'volume_horaire': int(request.data.get('volume_horaire', 4)),
        })
        return Response({'status': 'success'})

@api_view(['GET'])
def api_dashboard(request):
    return Response({
        'schools_count': len(instituts_col().find()),
        'matieres_count': len(matieres_col().find()),
        'teachers_count': len(enseignants_col().find()),
        'rooms_count': len(salles_col().find()),
        'classes_count': len(classes_col().find()),
    })

@api_view(['GET'])
def api_gouvernorats(request):
    return Response([{'code': code, 'label': label} for code, label in GOUVERNORATS])


# ---------------------------- CRUD EDIT / DELETE ---------------------------- #

@login_required_custom
def school_edit_view(request, school_id):
    school = instituts_col().find_one({'_id': school_id})
    if not school: return redirect('school_list')
    if request.method == 'POST':
        form = InstitutForm(request.POST)
        if form.is_valid():
            instituts_col().update_one({'_id': school_id}, {
                'nom': form.cleaned_data['nom'],
                'region': form.cleaned_data['region'],
                'ville': form.cleaned_data['ville'],
            })
            messages.success(request, 'École mise à jour.')
            return redirect('school_list')
    else:
        form = InstitutForm(initial=school)
    return render(request, 'schools/edit.html', {'form': form})

@login_required_custom
def school_delete_view(request, school_id):
    instituts_col().delete_one({'_id': school_id})
    messages.success(request, 'École supprimée.')
    return redirect('school_list')

@login_required_custom
def teacher_edit_view(request, teacher_id):
    teacher = enseignants_col().find_one({'_id': teacher_id})
    if not teacher: return redirect('school_list')
    school_id = teacher['institut_id']
    if request.method == 'POST':
        form = EnseignantForm(request.POST)
        if form.is_valid():
            enseignants_col().update_one({'_id': teacher_id}, {
                'nom': form.cleaned_data['nom'],
                'niveaux': form.cleaned_data['niveaux'],
                'volume_horaire': form.cleaned_data['volume_horaire'],
            })
            messages.success(request, 'Enseignant mis à jour.')
            return redirect('teacher_list', school_id=school_id)
    else:
        form = EnseignantForm(initial=teacher)
    return render(request, 'teachers/edit.html', {'form': form, 'school': resolve_institut(school_id)})

@login_required_custom
def teacher_delete_view(request, teacher_id):
    teacher = enseignants_col().find_one({'_id': teacher_id})
    if teacher:
        school_id = teacher['institut_id']
        enseignants_col().delete_one({'_id': teacher_id})
        messages.success(request, 'Enseignant supprimé.')
        return redirect('teacher_list', school_id=school_id)
    return redirect('school_list')

@login_required_custom
def room_edit_view(request, room_id):
    room = salles_col().find_one({'_id': room_id})
    if not room: return redirect('school_list')
    school_id = room['institut_id']
    if request.method == 'POST':
        form = SalleForm(request.POST)
        if form.is_valid():
            salles_col().update_one({'_id': room_id}, {
                'numero': form.cleaned_data['numero'],
                'type': form.cleaned_data['type'],
                'capacite': form.cleaned_data['capacite'],
            })
            messages.success(request, 'Salle mise à jour.')
            return redirect('room_list', school_id=school_id)
    else:
        form = SalleForm(initial=room)
    return render(request, 'rooms/edit.html', {'form': form, 'school': resolve_institut(school_id)})

@login_required_custom
def room_delete_view(request, room_id):
    room = salles_col().find_one({'_id': room_id})
    if room:
        school_id = room['institut_id']
        salles_col().delete_one({'_id': room_id})
        messages.success(request, 'Salle supprimée.')
        return redirect('room_list', school_id=school_id)
    return redirect('school_list')

@login_required_custom
def class_edit_view(request, class_id):
    classe = classes_col().find_one({'_id': class_id})
    if not classe: return redirect('school_list')
    school_id = classe['institut_id']
    if request.method == 'POST':
        form = ClasseForm(request.POST)
        if form.is_valid():
            classes_col().update_one({'_id': class_id}, {
                'niveau': int(form.cleaned_data['niveau']),
                'nom': form.cleaned_data['nom'],
            })
            messages.success(request, 'Classe mise à jour.')
            return redirect('class_list', school_id=school_id)
    else:
        form = ClasseForm(initial=classe)
    return render(request, 'classes/edit.html', {'form': form, 'school': resolve_institut(school_id)})

@login_required_custom
def class_delete_view(request, class_id):
    classe = classes_col().find_one({'_id': class_id})
    if classe:
        school_id = classe['institut_id']
        classes_col().delete_one({'_id': class_id})
        messages.success(request, 'Classe supprimée.')
        return redirect('class_list', school_id=school_id)
    return redirect('school_list')

# ---------------------------- 5. GESTION DES MATIÈRES ---------------------------- #

@login_required_custom
def matiere_list_view(request):
    matieres = get_all_matieres()
    return render(request, 'matieres/list.html', {'matieres': matieres})

@login_required_custom
def matiere_add_view(request):
    if request.method == 'POST':
        form = MatiereForm(request.POST)
        if form.is_valid():
            matieres_col().insert_one({
                'nom': form.cleaned_data['nom'],
                'niveaux': list(form.cleaned_data['niveaux']),
                'volume_horaire': form.cleaned_data['volume_horaire'],
            })
            messages.success(request, f"La matière '{form.cleaned_data['nom']}' a été ajoutée avec succès !")
            return redirect('matiere_list')
    else:
        form = MatiereForm()
    return render(request, 'matieres/add.html', {'form': form})

@login_required_custom
def matiere_edit_view(request, matiere_id):
    matiere = matieres_col().find_one({'_id': matiere_id})
    if not matiere:
        return redirect('matiere_list')
    if request.method == 'POST':
        form = MatiereForm(request.POST)
        if form.is_valid():
            matieres_col().update_one({'_id': matiere_id}, {
                'nom': form.cleaned_data['nom'],
                'niveaux': list(form.cleaned_data['niveaux']),
                'volume_horaire': form.cleaned_data['volume_horaire'],
            })
            messages.success(request, 'Matière mise à jour.')
            return redirect('matiere_list')
    else:
        initial = dict(matiere)
        # Forcer la liste pour le MultipleChoiceField
        initial['niveaux'] = [str(n) for n in matiere.get('niveaux', [])]
        form = MatiereForm(initial=initial)
    return render(request, 'matieres/edit.html', {'form': form, 'matiere': matiere})

@login_required_custom
def matiere_delete_view(request, matiere_id):
    matieres_col().delete_one({'_id': matiere_id})
    messages.success(request, 'Matière supprimée.')
    return redirect('matiere_list')


# ========================= DÉTECTION DE CONFLITS ========================= #

def _run_conflict_detection():
    """
    Algorithme central de détection de conflits d'emplois du temps.
    Croise DEUX sources de données :
      - emplois_du_temps (saisis via la page "Emploi du temps" de chaque CLASSE)
      - emplois_du_temps_enseignants (saisis via la page "Emploi du temps" de chaque ENSEIGNANT)
    Détecte :
      1. Conflit enseignant  : même enseignant affecté à 2 classes différentes sur le même créneau
      2. Conflit salle       : même salle occupée par 2 classes différentes sur le même créneau
      3. Conflit classe      : même classe avec 2 matières différentes sur le même créneau (doublon)
      4. Matière répétée     : même classe avec la MEME matière sur 2 créneaux différents le même jour
    Retourne un dict structuré avec les conflits par type.
    """
    # --- Chargement des données de référence ---
    enseignants_map = {e['id']: e.get('nom', 'Inconnu') for e in enseignants_col().find()}
    salles_map      = {s['id']: s.get('numero', '?')    for s in salles_col().find()}
    classes_map     = {c['id']: f"Niveau {c.get('niveau','')} – {c.get('nom','')}" for c in classes_col().find()}
    matieres_map    = {m['id']: m.get('nom', '?')       for m in matieres_col().find()}

    creneaux_labels = {
        '0': '08h00 – 10h00',
        '1': '10h15 – 12h15',
        '2': '14h00 – 16h00',
        '3': '16h15 – 18h00',
    }

    # --- Aplatir TOUTES les séances (des 2 sources) en une seule liste plate ---
    all_seances = []  # [{jour, creneau, classe_id, enseignant_id, salle_id, matiere_id, source}, ...]

    # SOURCE 1 : emplois du temps des CLASSES
    for emp in emplois_du_temps_col().find():
        classe_id = emp.get('classe_id', '')
        seances   = emp.get('seances', {})
        if not isinstance(seances, dict):
            continue
        for jour, slots in seances.items():
            if not isinstance(slots, dict):
                continue
            for creneau, data in slots.items():
                if not isinstance(data, dict):
                    continue
                ens_id   = data.get('enseignant_id', '').strip()
                salle_id = data.get('salle_id', '').strip()
                mat_id   = data.get('matiere_id', '').strip()
                if not ens_id and not salle_id and not mat_id:
                    continue
                all_seances.append({
                    'jour': jour, 'creneau': str(creneau),
                    'classe_id': classe_id, 'enseignant_id': ens_id,
                    'salle_id': salle_id, 'matiere_id': mat_id,
                    'source': 'classe',
                })

    # SOURCE 2 : emplois du temps des ENSEIGNANTS
    for emp in emplois_du_temps_enseignants_col().find():
        teacher_id = emp.get('teacher_id', '')
        seances    = emp.get('seances', {})
        if not isinstance(seances, dict):
            continue
        for jour, slots in seances.items():
            if not isinstance(slots, dict):
                continue
            for creneau, data in slots.items():
                if not isinstance(data, dict):
                    continue
                classe_id = data.get('classe_id', '').strip()
                salle_id  = data.get('salle_id', '').strip()
                mat_id    = data.get('matiere_id', '').strip()
                if not classe_id and not salle_id and not mat_id:
                    continue
                all_seances.append({
                    'jour': jour, 'creneau': str(creneau),
                    'classe_id': classe_id, 'enseignant_id': teacher_id,
                    'salle_id': salle_id, 'matiere_id': mat_id,
                    'source': 'enseignant',
                })

    # --- Regroupement par (jour, creneau) pour les conflits 1, 2, 3 ---
    slot_map = {}
    for s in all_seances:
        key = (s['jour'], s['creneau'])
        slot_map.setdefault(key, []).append(s)

    conflicts_enseignant = []
    conflicts_salle      = []
    conflicts_classe     = []

    for (jour, creneau), seances_list in slot_map.items():
        label_creneau = creneaux_labels.get(str(creneau), f"Créneau {creneau}")

        # ---- 1. Conflit Enseignant ----
        ens_usage = {}  # enseignant_id -> set(classe_id)
        for s in seances_list:
            if s['enseignant_id'] and s['classe_id']:
                ens_usage.setdefault(s['enseignant_id'], set()).add(s['classe_id'])
        for ens_id, classes_ids in ens_usage.items():
            if len(classes_ids) > 1:
                classes_ids = sorted(classes_ids)
                conflicts_enseignant.append({
                    'type':          'Conflit Enseignant',
                    'severite':      'danger',
                    'jour':          jour.capitalize(),
                    'creneau':       label_creneau,
                    'enseignant':    enseignants_map.get(ens_id, ens_id),
                    'enseignant_id': ens_id,
                    'classes':       [classes_map.get(cid, cid) for cid in classes_ids],
                    'message': (
                        f"L'enseignant « {enseignants_map.get(ens_id, ens_id)} » est affecté à "
                        f"{len(classes_ids)} classes simultanément le {jour.capitalize()} "
                        f"({label_creneau}) : "
                        + " & ".join(classes_map.get(cid, cid) for cid in classes_ids)
                    ),
                })

        # ---- 2. Conflit Salle ----
        salle_usage = {}  # salle_id -> set(classe_id)
        for s in seances_list:
            if s['salle_id'] and s['classe_id']:
                salle_usage.setdefault(s['salle_id'], set()).add(s['classe_id'])
        for sal_id, classes_ids in salle_usage.items():
            if len(classes_ids) > 1:
                classes_ids = sorted(classes_ids)
                conflicts_salle.append({
                    'type':      'Conflit Salle',
                    'severite':  'warning',
                    'jour':      jour.capitalize(),
                    'creneau':   label_creneau,
                    'salle':     f"Salle {salles_map.get(sal_id, sal_id)}",
                    'salle_id':  sal_id,
                    'classes':   [classes_map.get(cid, cid) for cid in classes_ids],
                    'message': (
                        f"La salle n°{salles_map.get(sal_id, sal_id)} est réservée par "
                        f"{len(classes_ids)} classes en même temps le {jour.capitalize()} "
                        f"({label_creneau}) : "
                        + " & ".join(classes_map.get(cid, cid) for cid in classes_ids)
                    ),
                })

        # ---- 3. Conflit Classe (2 matieres differentes sur le MEME creneau) ----
        classe_usage = {}  # classe_id -> set(matiere_id)
        for s in seances_list:
            if s['classe_id'] and s['matiere_id']:
                classe_usage.setdefault(s['classe_id'], set()).add(s['matiere_id'])
        for cls_id, matieres_ids in classe_usage.items():
            if len(matieres_ids) > 1:
                matieres_ids = sorted(matieres_ids)
                conflicts_classe.append({
                    'type':      'Conflit Classe',
                    'severite':  'info',
                    'jour':      jour.capitalize(),
                    'creneau':   label_creneau,
                    'classe':    classes_map.get(cls_id, cls_id),
                    'classe_id': cls_id,
                    'matieres':  [matieres_map.get(mid, mid) for mid in matieres_ids],
                    'message': (
                        f"La classe « {classes_map.get(cls_id, cls_id)} » a {len(matieres_ids)} cours "
                        f"en même temps le {jour.capitalize()} ({label_creneau}) : "
                        + " & ".join(matieres_map.get(mid, mid) for mid in matieres_ids)
                    ),
                })

    # ---- 4. Matière répétée le même jour (creneaux DIFFERENTS, meme matiere) ----
    conflicts_repetition = []
    # Regroupe par (classe_id, jour) -> matiere_id -> liste de creneaux distincts
    day_class_matiere = {}
    for s in all_seances:
        if not s['classe_id'] or not s['matiere_id']:
            continue
        key = (s['classe_id'], s['jour'])
        day_class_matiere.setdefault(key, {}).setdefault(s['matiere_id'], set()).add(s['creneau'])

    for (cls_id, jour), matieres_dict in day_class_matiere.items():
        for mat_id, creneaux_set in matieres_dict.items():
            if len(creneaux_set) > 1:
                creneaux_sorted = sorted(creneaux_set)
                labels = [creneaux_labels.get(c, f"Créneau {c}") for c in creneaux_sorted]
                conflicts_repetition.append({
                    'type':      'Matière Répétée',
                    'severite':  'warning',
                    'jour':      jour.capitalize(),
                    'creneau':   " & ".join(labels),
                    'classe':    classes_map.get(cls_id, cls_id),
                    'classe_id': cls_id,
                    'matiere':   matieres_map.get(mat_id, mat_id),
                    'matiere_id': mat_id,
                    'message': (
                        f"La classe « {classes_map.get(cls_id, cls_id)} » étudie "
                        f"« {matieres_map.get(mat_id, mat_id)} » {len(creneaux_sorted)} fois le "
                        f"{jour.capitalize()} : " + " puis ".join(labels)
                    ),
                })

    total = (
        len(conflicts_enseignant) + len(conflicts_salle)
        + len(conflicts_classe) + len(conflicts_repetition)
    )
    return {
        'total':                  total,
        'conflicts_enseignant':   conflicts_enseignant,
        'conflicts_salle':        conflicts_salle,
        'conflicts_classe':       conflicts_classe,
        'conflicts_repetition':   conflicts_repetition,
        'nb_enseignant':          len(conflicts_enseignant),
        'nb_salle':               len(conflicts_salle),
        'nb_classe':              len(conflicts_classe),
        'nb_repetition':          len(conflicts_repetition),
        'date_verification':      datetime.now().strftime('%d/%m/%Y à %H:%M:%S'),
    }
@login_required_custom
def detect_conflicts_view(request):
    """
    Vue principale de détection des conflits.
    GET  → affiche automatiquement le dernier rapport connu (généré par n8n ou manuellement)
    POST → relance l'analyse immédiatement, sauvegarde et affiche le nouveau rapport
    """
    from .db_service import get_latest_conflict_report, save_conflict_report

    if request.method == 'POST':
        result = _run_conflict_detection()
        save_conflict_report(result)
    else:
        result = get_latest_conflict_report()

    return render(request, 'conflicts/detect.html', {
        'result': result,
    })


@csrf_exempt
@api_view(['GET'])
def api_detect_conflicts(request):
    """
    Endpoint REST JSON pour le workflow n8n.
    GET /api/conflicts/
    Retourne le rapport complet de conflits en JSON.
    """
    result = _run_conflict_detection()
    return Response(result, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def api_save_conflicts(request):
    """
    Endpoint REST appelé par n8n après chaque vérification périodique.
    POST /api/conflicts/save/
    Sauvegarde le rapport reçu pour affichage automatique sur /conflicts/.
    """
    from .db_service import save_conflict_report
    save_conflict_report(request.data)
    return Response({'status': 'saved'}, status=status.HTTP_200_OK)
