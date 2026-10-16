class Teacher {
  final String id;
  final String schoolId;
  final String nom;
  final String niveaux;
  final int volumeHoraire;
  final String scheduleText;

  Teacher({
    required this.id,
    required this.schoolId,
    required this.nom,
    required this.niveaux,
    required this.volumeHoraire,
    required this.scheduleText,
  });

  factory Teacher.fromJson(Map<String, dynamic> json) {
    return Teacher(
      id: json['id'] ?? json['_id'] ?? '',
      schoolId: json['institut_id'] ?? json['school_id'] ?? '',
      nom: json['nom'] ?? '',
      niveaux: json['niveaux'] ?? 'Niveau 1, Niveau 2',
      volumeHoraire: json['volume_horaire'] is int ? json['volume_horaire'] : int.tryParse(json['volume_horaire']?.toString() ?? '18') ?? 18,
      scheduleText: json['schedule_text'] ?? 'Non renseigné',
    );
  }
}
