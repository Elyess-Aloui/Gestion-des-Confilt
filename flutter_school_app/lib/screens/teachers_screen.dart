import 'package:flutter/material.dart';
import '../models/school.dart';
import '../models/teacher.dart';
import '../services/api_service.dart';

class TeachersScreen extends StatefulWidget {
  final School? initialSchool;
  const TeachersScreen({super.key, this.initialSchool});

  @override
  State<TeachersScreen> createState() => _TeachersScreenState();
}

class _TeachersScreenState extends State<TeachersScreen> {
  List<School> _schools = [];
  School? _selectedSchool;
  List<Teacher> _teachers = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadInitialData();
  }

  Future<void> _loadInitialData() async {
    setState(() => _isLoading = true);
    final schools = await ApiService.getSchools();
    
    School? current;
    if (widget.initialSchool != null) {
      current = schools.firstWhere(
        (s) => s.id == widget.initialSchool!.id,
        orElse: () => schools.isNotEmpty ? schools.first : widget.initialSchool!,
      );
    } else if (schools.isNotEmpty) {
      current = schools.first;
    }

    List<Teacher> teachers = [];
    if (current != null) {
      teachers = await ApiService.getTeachers(current.id);
    }

    setState(() {
      _schools = schools;
      _selectedSchool = current;
      _teachers = teachers;
      _isLoading = false;
    });
  }

  Future<void> _loadTeachers() async {
    if (_selectedSchool == null) return;
    setState(() => _isLoading = true);
    final teachers = await ApiService.getTeachers(_selectedSchool!.id);
    setState(() {
      _teachers = teachers;
      _isLoading = false;
    });
  }

  void _showAddTeacherDialog() {
    if (_selectedSchool == null) return;
    final nomCtrl = TextEditingController();
    final niveauxCtrl = TextEditingController(text: "Niveau 1, Niveau 2");
    final volumeCtrl = TextEditingController(text: "18");
    final scheduleCtrl = TextEditingController(text: "Lundi - Vendredi: 08h00 - 16h00");

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.person_add, color: Color(0xFF4F46E5)),
            SizedBox(width: 8),
            Text("Ajouter un Enseignant", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text("Nom complet", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
              const SizedBox(height: 6),
              TextField(
                controller: nomCtrl,
                decoration: InputDecoration(
                  hintText: "Ex: M. Jean Dupont",
                  filled: true,
                  fillColor: const Color(0xFFF9FAFB),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFFD1D5DB))),
                ),
              ),
              const SizedBox(height: 14),
              const Text("Niveau(x) enseigné(s)", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
              const SizedBox(height: 6),
              TextField(
                controller: niveauxCtrl,
                decoration: InputDecoration(
                  hintText: "Ex: Niveau 1, Niveau 2, Niveau 3",
                  filled: true,
                  fillColor: const Color(0xFFF9FAFB),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFFD1D5DB))),
                ),
              ),
              const SizedBox(height: 14),
              const Text("Volume horaire hebdomadaire (heures max/semaine)", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
              const SizedBox(height: 6),
              TextField(
                controller: volumeCtrl,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  hintText: "Ex: 18",
                  filled: true,
                  fillColor: const Color(0xFFF9FAFB),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFFD1D5DB))),
                ),
              ),
              const SizedBox(height: 14),
              const Text("Disponibilité / Horaires", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
              const SizedBox(height: 6),
              TextField(
                controller: scheduleCtrl,
                decoration: InputDecoration(
                  hintText: "Ex: Lundi-Vendredi 08h-16h",
                  filled: true,
                  fillColor: const Color(0xFFF9FAFB),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFFD1D5DB))),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text("Annuler", style: TextStyle(color: Color(0xFF6B7280))),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF4F46E5),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            onPressed: () async {
              if (nomCtrl.text.trim().isNotEmpty) {
                final vol = int.tryParse(volumeCtrl.text.trim()) ?? 18;
                await ApiService.addTeacher(
                  _selectedSchool!.id,
                  nomCtrl.text.trim(),
                  niveauxCtrl.text.trim(),
                  vol,
                  scheduleCtrl.text.trim(),
                );
                if (ctx.mounted) Navigator.pop(ctx);
                _loadTeachers();
              }
            },
            child: const Text("Enregistrer"),
          ),
        ],
      ),
    );
  }

  void _showClaimAbsenceDialog(Teacher teacher) {
    final reasonCtrl = TextEditingController();
    final startCtrl = TextEditingController(text: DateTime.now().toString().split(' ')[0]);
    final endCtrl = TextEditingController(text: DateTime.now().add(const Duration(days: 1)).toString().split(' ')[0]);

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.event_busy, color: Color(0xFFEA580C)),
            const SizedBox(width: 8),
            Expanded(child: Text("Réclamation Absence - ${teacher.nom}", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text("Motif de l'absence", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
              const SizedBox(height: 6),
              TextField(
                controller: reasonCtrl,
                maxLines: 2,
                decoration: InputDecoration(
                  hintText: "Ex: Congé maladie, impératif familial...",
                  filled: true,
                  fillColor: const Color(0xFFF9FAFB),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
              const SizedBox(height: 14),
              const Text("Date de début (YYYY-MM-DD)", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
              const SizedBox(height: 6),
              TextField(
                controller: startCtrl,
                decoration: InputDecoration(
                  filled: true,
                  fillColor: const Color(0xFFF9FAFB),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
              const SizedBox(height: 14),
              const Text("Date de fin (YYYY-MM-DD)", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
              const SizedBox(height: 6),
              TextField(
                controller: endCtrl,
                decoration: InputDecoration(
                  filled: true,
                  fillColor: const Color(0xFFF9FAFB),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Annuler")),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEA580C),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            onPressed: () async {
              if (reasonCtrl.text.trim().isNotEmpty) {
                await ApiService.claimAbsence(teacher.id, reasonCtrl.text.trim(), startCtrl.text.trim(), endCtrl.text.trim());
                if (ctx.mounted) Navigator.pop(ctx);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text("Réclamation d'absence soumise avec succès.")),
                  );
                }
              }
            },
            child: const Text("Soumettre"),
          ),
        ],
      ),
    );
  }

  void _confirmDeleteTeacher(Teacher teacher) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text("Supprimer l'enseignant"),
        content: Text("Voulez-vous vraiment supprimer ${teacher.nom} ?"),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Annuler")),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFDC2626), foregroundColor: Colors.white),
            onPressed: () async {
              await ApiService.deleteTeacher(teacher.id);
              if (ctx.mounted) Navigator.pop(ctx);
              _loadTeachers();
            },
            child: const Text("Supprimer"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F6F8),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        title: const Text("Gestion des Enseignants", style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.bold, fontSize: 18)),
        iconTheme: const IconThemeData(color: Color(0xFF111827)),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadTeachers),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF4F46E5)))
          : Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // School Selector
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFE5E7EB)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.school, color: Color(0xFF4F46E5)),
                        const SizedBox(width: 12),
                        const Text("Établissement : ", style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF374151))),
                        Expanded(
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<School>(
                              isExpanded: true,
                              value: _selectedSchool,
                              hint: const Text("Sélectionnez une école"),
                              items: _schools.map((s) {
                                return DropdownMenuItem<School>(
                                  value: s,
                                  child: Text("${s.nom} (${s.ville})", style: const TextStyle(color: Color(0xFF111827))),
                                );
                              }).toList(),
                              onChanged: (School? s) {
                                setState(() => _selectedSchool = s);
                                _loadTeachers();
                              },
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Header bar
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text("Enseignants de l'établissement", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF111827))),
                          Text("${_teachers.length} enseignant(s) trouvé(s)", style: const TextStyle(fontSize: 13, color: Color(0xFF6B7280))),
                        ],
                      ),
                      if (_selectedSchool != null)
                        ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF4F46E5),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          ),
                          onPressed: _showAddTeacherDialog,
                          icon: const Icon(Icons.add, size: 18),
                          label: const Text("+ Ajouter Enseignant", style: TextStyle(fontWeight: FontWeight.w600)),
                        ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Teachers list
                  Expanded(
                    child: _selectedSchool == null
                        ? const Center(child: Text("Veuillez sélectionner un établissement."))
                        : _teachers.isEmpty
                            ? Center(
                                child: Container(
                                  padding: const EdgeInsets.all(32),
                                  decoration: BoxDecoration(
                                    color: Colors.white,
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(color: const Color(0xFFE5E7EB)),
                                  ),
                                  child: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Icon(Icons.person_outline, size: 48, color: Color(0xFF9CA3AF)),
                                      const SizedBox(height: 12),
                                      const Text("Aucun enseignant dans cet établissement", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF374151))),
                                      const SizedBox(height: 8),
                                      ElevatedButton(
                                        style: ElevatedButton.styleFrom(
                                          backgroundColor: const Color(0xFF4F46E5),
                                          foregroundColor: Colors.white,
                                        ),
                                        onPressed: _showAddTeacherDialog,
                                        child: const Text("Ajouter un enseignant"),
                                      ),
                                    ],
                                  ),
                                ),
                              )
                            : ListView.separated(
                                itemCount: _teachers.length,
                                separatorBuilder: (_, __) => const SizedBox(height: 12),
                                itemBuilder: (context, index) {
                                  final teacher = _teachers[index];
                                  return Container(
                                    padding: const EdgeInsets.all(16),
                                    decoration: BoxDecoration(
                                      color: Colors.white,
                                      borderRadius: BorderRadius.circular(12),
                                      border: Border.all(color: const Color(0xFFE5E7EB)),
                                      boxShadow: [
                                        BoxShadow(
                                          color: Colors.black.withValues(alpha: 0.02),
                                          blurRadius: 4,
                                          offset: const Offset(0, 2),
                                        )
                                      ],
                                    ),
                                    child: Row(
                                      children: [
                                        Container(
                                          width: 44,
                                          height: 44,
                                          decoration: BoxDecoration(
                                            color: const Color(0xFFE0E7FF),
                                            borderRadius: BorderRadius.circular(10),
                                          ),
                                          child: const Icon(Icons.person, color: Color(0xFF4338CA)),
                                        ),
                                        const SizedBox(width: 16),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Row(
                                                children: [
                                                  Text(
                                                    teacher.nom,
                                                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF111827)),
                                                  ),
                                                  const SizedBox(width: 8),
                                                  Container(
                                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                                    decoration: BoxDecoration(
                                                      color: const Color(0xFFEEF2FF),
                                                      borderRadius: BorderRadius.circular(6),
                                                      border: Border.all(color: const Color(0xFFC7D2FE)),
                                                    ),
                                                    child: Text(
                                                      teacher.niveaux,
                                                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF4338CA)),
                                                    ),
                                                  ),
                                                  const SizedBox(width: 8),
                                                  Container(
                                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                                    decoration: BoxDecoration(
                                                      color: const Color(0xFFF3F4F6),
                                                      borderRadius: BorderRadius.circular(6),
                                                      border: Border.all(color: const Color(0xFFE5E7EB)),
                                                    ),
                                                    child: Row(
                                                      mainAxisSize: MainAxisSize.min,
                                                      children: [
                                                        const Icon(Icons.timer_outlined, size: 12, color: Color(0xFF4B5563)),
                                                        const SizedBox(width: 3),
                                                        Text(
                                                          "${teacher.volumeHoraire} h/semaine",
                                                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF4B5563)),
                                                        ),
                                                      ],
                                                    ),
                                                  ),
                                                ],
                                              ),
                                              const SizedBox(height: 6),
                                              Row(
                                                children: [
                                                  const Icon(Icons.access_time, size: 14, color: Color(0xFF9CA3AF)),
                                                  const SizedBox(width: 4),
                                                  Text(
                                                    teacher.scheduleText,
                                                    style: const TextStyle(color: Color(0xFF6B7280), fontSize: 13),
                                                  ),
                                                ],
                                              ),
                                            ],
                                          ),
                                        ),
                                        TextButton.icon(
                                          style: TextButton.styleFrom(foregroundColor: const Color(0xFFEA580C)),
                                          onPressed: () => _showClaimAbsenceDialog(teacher),
                                          icon: const Icon(Icons.event_busy, size: 16),
                                          label: const Text("Absence", style: TextStyle(fontSize: 13)),
                                        ),
                                        IconButton(
                                          icon: const Icon(Icons.delete_outline, color: Color(0xFFDC2626)),
                                          tooltip: "Supprimer",
                                          onPressed: () => _confirmDeleteTeacher(teacher),
                                        ),
                                      ],
                                    ),
                                  );
                                },
                              ),
                  ),
                ],
              ),
            ),
    );
  }
}
