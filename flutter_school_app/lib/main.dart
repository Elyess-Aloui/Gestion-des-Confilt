import 'package:flutter/material.dart';
import 'models/school.dart';
import 'services/api_service.dart';
import 'screens/schools_screen.dart';
import 'screens/teachers_screen.dart';
import 'screens/rooms_screen.dart';
import 'screens/classes_screen.dart';
import 'screens/matieres_screen.dart';

void main() {
  runApp(const SchoolManagerApp());
}

class SchoolManagerApp extends StatelessWidget {
  const SchoolManagerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'EduManager - Gestion des emplois du temps',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF5F6F8),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF4F46E5),
          primary: const Color(0xFF4F46E5),
          surface: Colors.white,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          elevation: 0.5,
          iconTheme: IconThemeData(color: Color(0xFF111827)),
          titleTextStyle: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.bold, fontSize: 18),
        ),
      ),
      home: const DashboardScreen(),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<School> _schools = [];
  School? _selectedSchool;
  Map<String, int> _stats = {
    'schools_count': 0,
    'teachers_count': 0,
    'rooms_count': 0,
    'classes_count': 0,
  };
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    setState(() => _isLoading = true);
    final schools = await ApiService.getSchools();
    final stats = await ApiService.getDashboardStats();
    setState(() {
      _schools = schools;
      if (_schools.isNotEmpty && (_selectedSchool == null || !_schools.contains(_selectedSchool))) {
        _selectedSchool = _schools.first;
      }
      _stats = stats;
      _isLoading = false;
    });
  }

  void _showAddSchoolDialog() {
    final nomCtrl = TextEditingController();
    final villeCtrl = TextEditingController();
    String selectedRegion = 'tunis';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Row(
            children: [
              Icon(Icons.school, color: Color(0xFF4F46E5)),
              SizedBox(width: 8),
              Text("Ajouter une École", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text("Nom de l'établissement", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  controller: nomCtrl,
                  decoration: InputDecoration(
                    hintText: "Ex: Lycée Bourguiba",
                    filled: true,
                    fillColor: const Color(0xFFF9FAFB),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
                const SizedBox(height: 14),
                const Text("Région / Gouvernorat", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  decoration: InputDecoration(
                    hintText: "Ex: Tunis, Ariana...",
                    filled: true,
                    fillColor: const Color(0xFFF9FAFB),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  onChanged: (val) => selectedRegion = val,
                ),
                const SizedBox(height: 14),
                const Text("Ville", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  controller: villeCtrl,
                  decoration: InputDecoration(
                    hintText: "Ex: Tunis Centre",
                    filled: true,
                    fillColor: const Color(0xFFF9FAFB),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
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
                  await ApiService.addSchool(nomCtrl.text.trim(), selectedRegion, villeCtrl.text.trim());
                  if (ctx.mounted) Navigator.pop(ctx);
                  _loadDashboardData();
                }
              },
              child: const Text("Enregistrer"),
            ),
          ],
        ),
      ),
    );
  }

  void _navigateTo(Widget screen) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => screen),
    ).then((_) => _loadDashboardData());
  }

  @override
  Widget build(BuildContext context) {
    final isDesktop = MediaQuery.of(context).size.width > 800;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            const Icon(Icons.school, color: Color(0xFF4F46E5), size: 28),
            const SizedBox(width: 10),
            const Text(
              "EduManager",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20, color: Color(0xFF111827)),
            ),
            if (isDesktop) ...[
              const SizedBox(width: 32),
              _buildNavHeaderButton("Tableau de bord", Icons.dashboard_outlined, true, () {}),
              _buildNavHeaderButton("Écoles", Icons.account_balance_outlined, false, () => _navigateTo(const SchoolsScreen())),
              _buildNavHeaderButton("Matières", Icons.menu_book_outlined, false, () => _navigateTo(const MatieresScreen())),
              _buildNavHeaderButton("Enseignants", Icons.person_outline, false, () => _navigateTo(TeachersScreen(initialSchool: _selectedSchool))),
              _buildNavHeaderButton("Salles", Icons.meeting_room_outlined, false, () => _navigateTo(RoomsScreen(initialSchool: _selectedSchool))),
              _buildNavHeaderButton("Classes", Icons.groups_outlined, false, () => _navigateTo(ClassesScreen(initialSchool: _selectedSchool))),
            ]
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF4B5563)),
            tooltip: "Actualiser",
            onPressed: _loadDashboardData,
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF4F46E5)))
          : SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title & Subtitle
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Tableau de bord",
                            style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Color(0xFF111827)),
                          ),
                          SizedBox(height: 4),
                          Text(
                            "Accédez à vos 5 modules de gestion ci-dessous.",
                            style: TextStyle(fontSize: 14, color: Color(0xFF6B7280)),
                          ),
                        ],
                      ),
                      Wrap(
                        spacing: 8,
                        children: [
                          OutlinedButton.icon(
                            style: OutlinedButton.styleFrom(
                              foregroundColor: const Color(0xFF4F46E5),
                              side: const BorderSide(color: Color(0xFF4F46E5)),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            ),
                            icon: const Icon(Icons.add, size: 16),
                            label: const Text("Nouvelle école", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12)),
                            onPressed: _showAddSchoolDialog,
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),

                  // Quick Stats Row
                  _buildStatsSummary(),
                  const SizedBox(height: 24),

                  // 5 Modules Grid
                  LayoutBuilder(
                    builder: (context, constraints) {
                      int crossAxisCount = 3;
                      if (constraints.maxWidth < 650) {
                        crossAxisCount = 1;
                      } else if (constraints.maxWidth < 1000) {
                        crossAxisCount = 2;
                      }

                      return GridView.count(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        crossAxisCount: crossAxisCount,
                        crossAxisSpacing: 18,
                        mainAxisSpacing: 18,
                        childAspectRatio: crossAxisCount == 1 ? 1.65 : 0.95,
                        children: [
                          // Card 1: Écoles
                          _buildModuleCard(
                            stepNumber: "1",
                            icon: Icons.account_balance,
                            title: "Écoles",
                            badgeCount: _stats['schools_count'] ?? _schools.length,
                            description: "Gérer les établissements scolaires, leurs régions et leurs villes.",
                            primaryActionText: "+ Ajouter une école",
                            onPrimaryAction: _showAddSchoolDialog,
                            secondaryActionText: "Liste des écoles",
                            onSecondaryAction: () => _navigateTo(const SchoolsScreen()),
                          ),

                          // Card 2: Matières
                          _buildModuleCard(
                            stepNumber: "2",
                            icon: Icons.menu_book,
                            title: "Matières",
                            badgeCount: _stats['matieres_count'] ?? 0,
                            description: "Configurer les matières, les 6 niveaux associés et volumes horaires.",
                            primaryActionText: "Accéder aux Matières",
                            onPrimaryAction: () => _navigateTo(const MatieresScreen()),
                          ),

                          // Card 3: Enseignants
                          _buildModuleCard(
                            stepNumber: "3",
                            icon: Icons.person_outline,
                            title: "Enseignants",
                            badgeCount: _stats['teachers_count'] ?? 0,
                            description: "Gérer le corps enseignant, disponibilités et réclamations d'absence.",
                            primaryActionText: "Accéder aux Enseignants",
                            onPrimaryAction: () => _navigateTo(TeachersScreen(initialSchool: _selectedSchool)),
                          ),

                          // Card 4: Salles
                          _buildModuleCard(
                            stepNumber: "4",
                            icon: Icons.meeting_room_outlined,
                            title: "Salles de cours",
                            badgeCount: _stats['rooms_count'] ?? 0,
                            description: "Contrôler la capacité des salles, leurs types et déclarer les pannes.",
                            primaryActionText: "Accéder aux Salles",
                            onPrimaryAction: () => _navigateTo(RoomsScreen(initialSchool: _selectedSchool)),
                          ),

                          // Card 5: Classes
                          _buildModuleCard(
                            stepNumber: "5",
                            icon: Icons.groups_outlined,
                            title: "Classes & Planning",
                            badgeCount: _stats['classes_count'] ?? 0,
                            description: "Gérer les classes, emplois du temps et export PDF officiel.",
                            primaryActionText: "Accéder aux Classes",
                            onPrimaryAction: () => _navigateTo(ClassesScreen(initialSchool: _selectedSchool)),
                          ),
                        ],
                      );
                    },
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildStatsSummary() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE5E7EB)),
      ),
      child: Row(
        children: [
          _buildStatItem("Écoles", _stats['schools_count'] ?? _schools.length, Icons.school_outlined),
          const SizedBox(width: 8),
          _buildStatDivider(),
          const SizedBox(width: 8),
          _buildStatItem("Matières", _stats['matieres_count'] ?? 0, Icons.menu_book_outlined),
          const SizedBox(width: 8),
          _buildStatDivider(),
          const SizedBox(width: 8),
          _buildStatItem("Enseignants", _stats['teachers_count'] ?? 0, Icons.people_outline),
          const SizedBox(width: 8),
          _buildStatDivider(),
          const SizedBox(width: 8),
          _buildStatItem("Salles", _stats['rooms_count'] ?? 0, Icons.meeting_room_outlined),
          const SizedBox(width: 8),
          _buildStatDivider(),
          const SizedBox(width: 8),
          _buildStatItem("Classes", _stats['classes_count'] ?? 0, Icons.calendar_month_outlined),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, int value, IconData icon) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: Color(0xFF6B7280)),
          ),
          const SizedBox(height: 2),
          Text(
            "$value",
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF4F46E5)),
          ),
        ],
      ),
    );
  }

  Widget _buildStatDivider() {
    return Container(
      width: 1,
      height: 28,
      color: const Color(0xFFE5E7EB),
    );
  }

  Widget _buildNavHeaderButton(String label, IconData icon, bool isActive, VoidCallback onTap) {
    return TextButton.icon(
      onPressed: onTap,
      icon: Icon(icon, size: 18, color: isActive ? const Color(0xFF4F46E5) : const Color(0xFF4B5563)),
      label: Text(
        label,
        style: TextStyle(
          color: isActive ? const Color(0xFF4F46E5) : const Color(0xFF4B5563),
          fontWeight: isActive ? FontWeight.bold : FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildModuleCard({
    required String stepNumber,
    required IconData icon,
    required String title,
    required int badgeCount,
    required String description,
    required String primaryActionText,
    required VoidCallback onPrimaryAction,
    String? secondaryActionText,
    VoidCallback? onSecondaryAction,
  }) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE5E7EB)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.025),
            blurRadius: 8,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: Step circle, Title, and Badge
          Row(
            children: [
              Container(
                width: 30,
                height: 30,
                decoration: const BoxDecoration(
                  color: Color(0xFF4F46E5),
                  shape: BoxShape.circle,
                ),
                alignment: Alignment.center,
                child: Text(
                  stepNumber,
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF111827)),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFFEEF2FF),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFC7D2FE)),
                ),
                child: Text(
                  "$badgeCount",
                  style: const TextStyle(color: Color(0xFF4338CA), fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),

          // Description
          Text(
            description,
            style: const TextStyle(fontSize: 12.5, color: Color(0xFF6B7280), height: 1.35),
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
          ),
          const Spacer(),

          // Secondary button if available
          if (secondaryActionText != null && onSecondaryAction != null) ...[
            OutlinedButton(
              style: OutlinedButton.styleFrom(
                foregroundColor: const Color(0xFF374151),
                side: const BorderSide(color: Color(0xFFD1D5DB)),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              ),
              onPressed: onSecondaryAction,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(secondaryActionText, style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 12)),
                  const Icon(Icons.arrow_forward_ios, size: 12, color: Color(0xFF9CA3AF)),
                ],
              ),
            ),
            const SizedBox(height: 6),
          ],

          // Primary action button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF4F46E5),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 10),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              onPressed: onPrimaryAction,
              child: Text(
                primaryActionText,
                style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12.5),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

