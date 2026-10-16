class SchoolClass {
  final String id;
  final String schoolId;
  final String nomClasse;
  final int niveau;
  final String niveauDisplay;
  final Map<String, dynamic>? emploiDuTemps;

  SchoolClass({
    required this.id,
    required this.schoolId,
    required this.nomClasse,
    required this.niveau,
    required this.niveauDisplay,
    this.emploiDuTemps,
  });

  factory SchoolClass.fromJson(Map<String, dynamic> json) {
    return SchoolClass(
      id: json['id'] ?? json['_id'] ?? '',
      schoolId: json['institut_id'] ?? json['school_id'] ?? '',
      nomClasse: json['nom'] ?? json['nom_classe'] ?? '',
      niveau: json['niveau'] is int ? json['niveau'] : int.tryParse(json['niveau'].toString()) ?? 1,
      niveauDisplay: json['niveau_display'] ?? 'Niveau ${json['niveau'] ?? 1}',
      emploiDuTemps: json['emploi_du_temps'],
    );
  }
}
