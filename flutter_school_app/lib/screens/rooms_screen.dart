import 'package:flutter/material.dart';
import '../models/school.dart';
import '../models/room.dart';
import '../services/api_service.dart';

class RoomsScreen extends StatefulWidget {
  final School? initialSchool;
  const RoomsScreen({super.key, this.initialSchool});

  @override
  State<RoomsScreen> createState() => _RoomsScreenState();
}

class _RoomsScreenState extends State<RoomsScreen> {
  List<School> _schools = [];
  School? _selectedSchool;
  List<Room> _rooms = [];
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

    List<Room> rooms = [];
    if (current != null) {
      rooms = await ApiService.getRooms(current.id);
    }

    setState(() {
      _schools = schools;
      _selectedSchool = current;
      _rooms = rooms;
      _isLoading = false;
    });
  }

  Future<void> _loadRooms() async {
    if (_selectedSchool == null) return;
    setState(() => _isLoading = true);
    final rooms = await ApiService.getRooms(_selectedSchool!.id);
    setState(() {
      _rooms = rooms;
      _isLoading = false;
    });
  }

  void _showAddRoomDialog() {
    if (_selectedSchool == null) return;
    final numCtrl = TextEditingController();
    final capCtrl = TextEditingController(text: "30");
    String selectedType = 'normale';

    final types = [
      {'code': 'normale', 'label': 'Salle de classe (normale)'},
      {'code': 'informatique', 'label': 'Salle informatique'},
      {'code': 'sport', 'label': 'Salle de sport'},
    ];

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Row(
            children: [
              Icon(Icons.meeting_room, color: Color(0xFF4F46E5)),
              SizedBox(width: 8),
              Text("Ajouter une Salle", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text("Numéro / Nom de la salle", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  controller: numCtrl,
                  decoration: InputDecoration(
                    hintText: "Ex: Salle 101, Labo 2",
                    filled: true,
                    fillColor: const Color(0xFFF9FAFB),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFFD1D5DB))),
                  ),
                ),
                const SizedBox(height: 14),
                const Text("Type de salle", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 6),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF9FAFB),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFFD1D5DB)),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      isExpanded: true,
                      value: selectedType,
                      items: types.map((t) {
                        return DropdownMenuItem<String>(
                          value: t['code'],
                          child: Text(t['label']!),
                        );
                      }).toList(),
                      onChanged: (val) {
                        if (val != null) {
                          setDialogState(() => selectedType = val);
                        }
                      },
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                const Text("Capacité (nombre de places)", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  controller: capCtrl,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    hintText: "Ex: 30",
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
                if (numCtrl.text.trim().isNotEmpty) {
                  final cap = int.tryParse(capCtrl.text.trim()) ?? 30;
                  await ApiService.addRoom(_selectedSchool!.id, numCtrl.text.trim(), selectedType, cap);
                  if (ctx.mounted) Navigator.pop(ctx);
                  _loadRooms();
                }
              },
              child: const Text("Enregistrer"),
            ),
          ],
        ),
      ),
    );
  }

  void _showToggleBreakdownDialog(Room room) {
    if (room.isBroken) {
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Text("Rétablir la salle"),
          content: Text("Marquer la salle '${room.numero}' comme disponible et fonctionnelle ?"),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Annuler")),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF16A34A), foregroundColor: Colors.white),
              onPressed: () async {
                await ApiService.toggleRoomBreakdown(room.id, '');
                if (ctx.mounted) Navigator.pop(ctx);
                _loadRooms();
              },
              child: const Text("Rétablir"),
            ),
          ],
        ),
      );
    } else {
      final durationCtrl = TextEditingController(text: "2 jours");
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: Row(
            children: [
              const Icon(Icons.warning_amber_rounded, color: Color(0xFFDC2626)),
              const SizedBox(width: 8),
              Text("Déclarer panne - ${room.numero}"),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text("Durée estimée de la panne :", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
              const SizedBox(height: 6),
              TextField(
                controller: durationCtrl,
                decoration: InputDecoration(
                  hintText: "Ex: 3 jours, 1 semaine...",
                  filled: true,
                  fillColor: const Color(0xFFF9FAFB),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Annuler")),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFDC2626), foregroundColor: Colors.white),
              onPressed: () async {
                await ApiService.toggleRoomBreakdown(room.id, durationCtrl.text.trim());
                if (ctx.mounted) Navigator.pop(ctx);
                _loadRooms();
              },
              child: const Text("Marquer en panne"),
            ),
          ],
        ),
      );
    }
  }

  void _confirmDeleteRoom(Room room) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text("Supprimer la salle"),
        content: Text("Voulez-vous vraiment supprimer la salle '${room.numero}' ?"),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Annuler")),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFDC2626), foregroundColor: Colors.white),
            onPressed: () async {
              await ApiService.deleteRoom(room.id);
              if (ctx.mounted) Navigator.pop(ctx);
              _loadRooms();
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
        title: const Text("Gestion des Salles", style: TextStyle(color: Color(0xFF111827), fontWeight: FontWeight.bold, fontSize: 18)),
        iconTheme: const IconThemeData(color: Color(0xFF111827)),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadRooms),
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
                                _loadRooms();
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
                          const Text("Salles de l'établissement", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF111827))),
                          Text("${_rooms.length} salle(s) répertoriée(s)", style: const TextStyle(fontSize: 13, color: Color(0xFF6B7280))),
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
                          onPressed: _showAddRoomDialog,
                          icon: const Icon(Icons.add, size: 18),
                          label: const Text("+ Ajouter Salle", style: TextStyle(fontWeight: FontWeight.w600)),
                        ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Rooms list
                  Expanded(
                    child: _selectedSchool == null
                        ? const Center(child: Text("Veuillez sélectionner un établissement."))
                        : _rooms.isEmpty
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
                                      const Icon(Icons.meeting_room_outlined, size: 48, color: Color(0xFF9CA3AF)),
                                      const SizedBox(height: 12),
                                      const Text("Aucune salle dans cet établissement", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF374151))),
                                      const SizedBox(height: 8),
                                      ElevatedButton(
                                        style: ElevatedButton.styleFrom(
                                          backgroundColor: const Color(0xFF4F46E5),
                                          foregroundColor: Colors.white,
                                        ),
                                        onPressed: _showAddRoomDialog,
                                        child: const Text("Ajouter une salle"),
                                      ),
                                    ],
                                  ),
                                ),
                              )
                            : ListView.separated(
                                itemCount: _rooms.length,
                                separatorBuilder: (_, __) => const SizedBox(height: 12),
                                itemBuilder: (context, index) {
                                  final room = _rooms[index];
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
                                            color: room.isBroken ? const Color(0xFFFEE2E2) : const Color(0xFFDCFCE7),
                                            borderRadius: BorderRadius.circular(10),
                                          ),
                                          child: Icon(
                                            room.isBroken ? Icons.report_problem : Icons.door_front_door,
                                            color: room.isBroken ? const Color(0xFFDC2626) : const Color(0xFF16A34A),
                                          ),
                                        ),
                                        const SizedBox(width: 16),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Row(
                                                children: [
                                                  Text(
                                                    room.numero,
                                                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF111827)),
                                                  ),
                                                  const SizedBox(width: 8),
                                                  Text(
                                                    "(${room.typeDisplay})",
                                                    style: const TextStyle(color: Color(0xFF6B7280), fontSize: 13),
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
                                                        const Icon(Icons.people_outline, size: 12, color: Color(0xFF4B5563)),
                                                        const SizedBox(width: 3),
                                                        Text(
                                                          "${room.capacite} places",
                                                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF4B5563)),
                                                        ),
                                                      ],
                                                    ),
                                                  ),
                                                ],
                                              ),
                                              const SizedBox(height: 6),
                                              if (room.isBroken && room.brokenDuration.isNotEmpty)
                                                Text(
                                                  "Durée estimée : ${room.brokenDuration}",
                                                  style: const TextStyle(color: Color(0xFFDC2626), fontSize: 12, fontWeight: FontWeight.w500),
                                                ),
                                            ],
                                          ),
                                        ),
                                        // Status badge button
                                        InkWell(
                                          onTap: () => _showToggleBreakdownDialog(room),
                                          borderRadius: BorderRadius.circular(6),
                                          child: Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                            decoration: BoxDecoration(
                                              color: room.isBroken ? const Color(0xFFFEE2E2) : const Color(0xFFDCFCE7),
                                              borderRadius: BorderRadius.circular(6),
                                              border: Border.all(color: room.isBroken ? const Color(0xFFFCA5A5) : const Color(0xFF86EFAC)),
                                            ),
                                            child: Row(
                                              mainAxisSize: MainAxisSize.min,
                                              children: [
                                                Icon(
                                                  room.isBroken ? Icons.error_outline : Icons.check_circle_outline,
                                                  size: 14,
                                                  color: room.isBroken ? const Color(0xFFDC2626) : const Color(0xFF15803D),
                                                ),
                                                const SizedBox(width: 4),
                                                Text(
                                                  room.isBroken ? "En panne" : "Disponible",
                                                  style: TextStyle(
                                                    fontWeight: FontWeight.bold,
                                                    fontSize: 12,
                                                    color: room.isBroken ? const Color(0xFFDC2626) : const Color(0xFF15803D),
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        IconButton(
                                          icon: const Icon(Icons.delete_outline, color: Color(0xFFDC2626)),
                                          tooltip: "Supprimer",
                                          onPressed: () => _confirmDeleteRoom(room),
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
