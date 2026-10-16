from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # 1. Gestion des Écoles
    path('schools/', views.school_list_view, name='school_list'),
    path('schools/add/', views.school_add_view, name='school_add'),
    path('schools/<str:school_id>/edit/', views.school_edit_view, name='school_edit'),
    path('schools/<str:school_id>/delete/', views.school_delete_view, name='school_delete'),

    # 2. Gestion des Enseignants
    path('teachers/select-school/', views.teacher_school_select_view, name='teacher_school_select'),
    path('schools/<str:school_id>/teachers/', views.teacher_list_view, name='teacher_list'),
    path('schools/<str:school_id>/teachers/add/', views.teacher_add_view, name='teacher_add'),
    path('teachers/<str:teacher_id>/edit/', views.teacher_edit_view, name='teacher_edit'),
    path('teachers/<str:teacher_id>/delete/', views.teacher_delete_view, name='teacher_delete'),
    path('teachers/<str:teacher_id>/timetable/', views.teacher_timetable_view, name='teacher_timetable'),
    path('teachers/<str:teacher_id>/download-timetable/', views.download_teacher_timetable_pdf_view, name='download_teacher_timetable'),
    path('teachers/<str:teacher_id>/claim-absence/', views.absence_claim_add_view, name='absence_claim_add'),

    # 3. Gestion des Salles
    path('rooms/select-school/', views.room_school_select_view, name='room_school_select'),
    path('schools/<str:school_id>/rooms/', views.room_list_view, name='room_list'),
    path('schools/<str:school_id>/rooms/add/', views.room_add_view, name='room_add'),
    path('rooms/<str:room_id>/edit/', views.room_edit_view, name='room_edit'),
    path('rooms/<str:room_id>/delete/', views.room_delete_view, name='room_delete'),
    path('rooms/<str:room_id>/mark-broken/', views.room_mark_broken_view, name='room_mark_broken'),

    # 4. Gestion des Classes
    path('classes/select-school/', views.class_school_select_view, name='class_school_select'),
    path('schools/<str:school_id>/classes/', views.class_list_view, name='class_list'),
    path('schools/<str:school_id>/classes/add/', views.class_add_view, name='class_add'),
    path('classes/<str:class_id>/edit/', views.class_edit_view, name='class_edit'),
    path('classes/<str:class_id>/delete/', views.class_delete_view, name='class_delete'),
    path('classes/<str:class_id>/timetable/', views.class_timetable_view, name='class_timetable'),
    path('classes/<str:class_id>/download-timetable/', views.download_class_timetable_pdf_view, name='download_class_timetable'),

    # REST API for Flutter client
    path('api/login/', views.api_login, name='api_login'),
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/dashboard/', views.api_dashboard, name='api_dashboard'),
    path('api/matieres/', views.api_matieres, name='api_matieres'),
    path('api/gouvernorats/', views.api_gouvernorats, name='api_gouvernorats'),
    path('api/schools/', views.api_schools, name='api_schools'),
    path('api/schools/<str:school_id>/', views.api_delete_school, name='api_delete_school'),
    path('api/schools/<str:school_id>/teachers/', views.api_teachers, name='api_teachers'),
    path('api/teachers/<str:teacher_id>/', views.api_delete_teacher, name='api_delete_teacher'),
    path('api/teachers/<str:teacher_id>/timetable/', views.api_teacher_timetable, name='api_teacher_timetable'),
    path('api/teachers/<str:teacher_id>/claim/', views.api_claim_absence, name='api_claim_absence'),
    path('api/schools/<str:school_id>/rooms/', views.api_rooms, name='api_rooms'),
    path('api/rooms/<str:room_id>/', views.api_delete_room, name='api_delete_room'),
    path('api/rooms/<str:room_id>/breakdown/', views.api_room_breakdown, name='api_room_breakdown'),
    path('api/schools/<str:school_id>/classes/', views.api_classes, name='api_classes'),
    path('api/classes/<str:class_id>/', views.api_delete_class, name='api_delete_class'),
    path('api/classes/<str:class_id>/timetable/', views.api_class_timetable, name='api_class_timetable'),
    path('api/classes/<str:class_id>/update-schedule/', views.api_update_class_schedule, name='api_update_class_schedule'),

    # 5. Gestion des Matières
    path('matieres/', views.matiere_list_view, name='matiere_list'),
    path('matieres/add/', views.matiere_add_view, name='matiere_add'),
    path('matieres/<str:matiere_id>/edit/', views.matiere_edit_view, name='matiere_edit'),
    path('matieres/<str:matiere_id>/delete/', views.matiere_delete_view, name='matiere_delete'),

    # REST API – Matières
    path('api/matieres/<str:matiere_id>/', views.api_matiere_detail, name='api_matiere_detail'),

        # 6. Détection des Conflits d'Emplois du Temps
    path('conflicts/', views.detect_conflicts_view, name='detect_conflicts'),
    path('api/conflicts/', views.api_detect_conflicts, name='api_detect_conflicts'),
    path('api/conflicts/save/', views.api_save_conflicts, name='api_save_conflicts'),
]
