class Matiere {
  final String id;
  final String nom;
  final List<String> niveaux;
  final int volumeHoraire;
  final String niveauxDisplay;

  Matiere({
    required this.id,
    required this.nom,
    required this.niveaux,
    required this.volumeHoraire,
    required this.niveauxDisplay,
  });

  factory Matiere.fromJson(Map<String, dynamic> json) {
    // niveaux may arrive as List<dynamic> or String
    List<String> niveauxList;
    final raw = json['niveaux'];
    if (raw is List) {
      niveauxList = raw.map((e) => e.toString()).toList();
    } else if (raw is String) {
      niveauxList = raw.split(',').map((e) => e.trim()).where((e) => e.isNotEmpty).toList();
    } else {
      niveauxList = [];
    }

    final volumeHoraire = json['volume_horaire'] is int
        ? json['volume_horaire'] as int
        : int.tryParse(json['volume_horaire']?.toString() ?? '4') ?? 4;

    final niveauxDisplay = json['niveaux_display'] as String? ??
        niveauxList.map((n) => 'Niveau $n').join(', ');

    return Matiere(
      id: json['id']?.toString() ?? json['_id']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      niveaux: niveauxList,
      volumeHoraire: volumeHoraire,
      niveauxDisplay: niveauxDisplay,
    );
  }
}
