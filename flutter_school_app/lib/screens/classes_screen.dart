import 'package:flutter/material.dart';
import '../models/school.dart';
import '../models/school_class.dart';
import '../services/api_service.dart';

class ClassesScreen extends StatefulWidget {
  final School? initialSchool;
  const ClassesScreen({super.key, this.initialSchool});

  @override
  State<ClassesScreen> createState() => _ClassesScreenState();
}

class _ClassesScreenState extends State<ClassesScreen> {
  List<School> _schools = [];
  School? _selectedSchool;
  List<SchoolClass> _classes = [];
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
      current = schools.firstWhere((s) => s.id == widget.initialSchool!.id, orElse: () => schools.isNotEmpty ? schools.first : widget.initialSchool!);
    } else if (schools.isNotEmpty) {
      current = schools.first;
    }

    List<SchoolClass> classes = [];
    if (current != null) {
      classes = await ApiService.getClasses(current.id);
    }

    setState(() {
      _schools = schools;
      _selectedSchool = current;
      _classes = classes;
      _isLoading = false;
    });
  }

  Future<void> _loadClasses() async {
    if (_selectedSchool == null) return;
    setState(() => _isLoading = true);
    final classes = await ApiService.getClasses(_selectedSchool!.id);
    setState(() {
      _classes = classes;
      _isLoading = false;
    });
  }

  void _showAddClassDialog() {
    if (_selectedSchool == null) return;
    final nomCtrl = TextEditingController();
    int selectedNiveau = 1;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Row(
            children: [
              Icon(Icons.class_, color: Color(0xFF4F46E5)),
              SizedBox(width: 8),
              Text("Ajouter une Classe", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text("Nom de la classe", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  controller: nomCtrl,
                  decoration: InputDecoration(
                    hintText: "Ex: 1ère Année A, Terminale S2",
                    filled: true,
                    fillColor: const Color(0xFFF9FAFB),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFFD1D5DB))),
                  ),
                ),
                const SizedBox(height: 14),
                const Text("Niveau", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 6),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF9FAFB),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFFD1D5DB)),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<int>(
                      isExpanded: true,
                      value: selectedNiveau,
                      items: [1, 2, 3, 4, 5, 6].map((n) {
                        return DropdownMenuItem<int>(
                          value: n,
                          child: Text("Niveau $n"),
                        );
                      }).toList(),
                      onChanged: (val) {
                        if (val != null) {
                          setDialogState(() => selectedNiveau = val);
                        }
                      },
                    ),
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
                  await ApiService.addClass(_selectedSchool!.id, nomCtrl.text.trim(), selectedNiveau);
                  if (ctx.mounted) Navigator.pop(ctx);
                  _loadClasses();
                }
              },
              child: const Text("Enregistrer"),
            ),
          ],
        ),
      ),
    );
  }

  void _showScheduleDialog(SchoolClass classe) {
    final scheduleCtrl = TextEditingController(
      text: classe.emploiDuTemps != null ? classe.emploiDuTemps.toString() : "Lundi: 08h-10h Math (Salle 101), 10h-12h Physique\nMardi: 08h-10h Français, 10h-12h Anglais",
    );

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.calendar_month, color: Color(0xFF4F46E5)),
            const SizedBox(width: 8),
            Expanded(child: Text("Emploi du temps - ${classe.nomClasse}", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text("Planning hebdomadaire :", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
            const SizedBox(height: 8),
            TextField(
              controller: scheduleCtrl,
              maxLines: 5,
              decoration: InputDecoration(
                filled: true,
                fillColor: const Color(0xFFF9FAFB),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Fermer")),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF4F46E5), foregroundColor: Colors.white),
            onPressed: () async {
              await ApiService.updateClassSchedule(classe.id, scheduleCtrl.text.trim());
              if (ctx.mounted) Navigator.pop(ctx);
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text("Emploi du temps mis à jour avec succès.")),
                );
              }
            },
            child: const Text("Enregistrer"),
          ),
        ],
      ),
    );
  }

  void _confirmDeleteClass(SchoolClass classe) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text("Supprimer la classe"),
        content: Text("Voulez-vous vraiment supprimer la classe '${classe.nomClasse}' ?"),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Annuler")),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFDC2626), foregroundColor: Colors.white),
            onPressed: () async {
              await ApiService.deleteClass(classe.id);
              if (ctx.mounted) Navigator.pop(ctx);
              _loadClasses();
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
        title: const Text("Gestion des Classes", style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.bold, fontSize: 18)),
        iconTheme: const IconThemeData(color: Color(0xFF111827)),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadClasses),
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
                                _loadClasses();
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
                          const Text("Classes de l'établissement", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF111827))),
                          Text("${_classes.length} classe(s) trouvée(s)", style: const TextStyle(fontSize: 13, color: Color(0xFF6B7280))),
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
                          onPressed: _showAddClassDialog,
                          icon: const Icon(Icons.add, size: 18),
                          label: const Text("+ Ajouter Classe", style: TextStyle(fontWeight: FontWeight.w600)),
                        ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Classes list
                  Expanded(
                    child: _selectedSchool == null
                        ? const Center(child: Text("Veuillez sélectionner un établissement."))
                        : _classes.isEmpty
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
                                      const Icon(Icons.groups_outlined, size: 48, color: Color(0xFF9CA3AF)),
                                      const SizedBox(height: 12),
                                      const Text("Aucune classe dans cet établissement", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF374151))),
                                      const SizedBox(height: 8),
                                      ElevatedButton(
                                        style: ElevatedButton.styleFrom(
                                          backgroundColor: const Color(0xFF4F46E5),
                                          foregroundColor: Colors.white,
                                        ),
                                        onPressed: _showAddClassDialog,
                                        child: const Text("Ajouter une classe"),
                                      ),
                                    ],
                                  ),
                                ),
                              )
                            : ListView.separated(
                                itemCount: _classes.length,
                                separatorBuilder: (_, __) => const SizedBox(height: 12),
                                itemBuilder: (context, index) {
                                  final classe = _classes[index];
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
                                            color: const Color(0xFFFDF2F8),
                                            borderRadius: BorderRadius.circular(10),
                                          ),
                                          child: const Icon(Icons.groups, color: Color(0xFFDB2777)),
                                        ),
                                        const SizedBox(width: 16),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Row(
                                                children: [
                                                  Text(
                                                    classe.nomClasse,
                                                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF111827)),
                                                  ),
                                                  const SizedBox(width: 8),
                                                  Container(
                                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                                    decoration: BoxDecoration(
                                                      color: const Color(0xFFF3F4F6),
                                                      borderRadius: BorderRadius.circular(6),
                                                      border: Border.all(color: const Color(0xFFE5E7EB)),
                                                    ),
                                                    child: Text(
                                                      classe.niveauDisplay,
                                                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF4B5563)),
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ],
                                          ),
                                        ),
                                        TextButton.icon(
                                          style: TextButton.styleFrom(foregroundColor: const Color(0xFF4F46E5)),
                                          onPressed: () => _showScheduleDialog(classe),
                                          icon: const Icon(Icons.calendar_month, size: 16),
                                          label: const Text("Emploi du temps", style: TextStyle(fontSize: 13)),
                                        ),
                                        IconButton(
                                          icon: const Icon(Icons.delete_outline, color: Color(0xFFDC2626)),
                                          tooltip: "Supprimer",
                                          onPressed: () => _confirmDeleteClass(classe),
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
