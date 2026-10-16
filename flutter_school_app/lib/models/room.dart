class Room {
  final String id;
  final String schoolId;
  final String numero;
  final String type;
  final String typeDisplay;
  final int capacite;
  final bool isBroken;
  final String brokenDuration;

  Room({
    required this.id,
    required this.schoolId,
    required this.numero,
    required this.type,
    required this.typeDisplay,
    required this.capacite,
    required this.isBroken,
    required this.brokenDuration,
  });

  factory Room.fromJson(Map<String, dynamic> json) {
    return Room(
      id: json['id'] ?? json['_id'] ?? '',
      schoolId: json['institut_id'] ?? json['school_id'] ?? '',
      numero: json['numero'] ?? json['nom_salle'] ?? '',
      type: json['type'] ?? 'normale',
      typeDisplay: json['type_display'] ?? json['type'] ?? 'Normale',
      capacite: json['capacite'] is int ? json['capacite'] : int.tryParse(json['capacite']?.toString() ?? '30') ?? 30,
      isBroken: json['is_broken'] == true,
      brokenDuration: json['broken_duration'] ?? '',
    );
  }
}
