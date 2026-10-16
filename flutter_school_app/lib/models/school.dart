class School {
  final String id;
  final String nom;
  final String region;
  final String ville;
  final String regionDisplay;

  School({
    required this.id,
    required this.nom,
    required this.region,
    required this.ville,
    this.regionDisplay = '',
  });

  factory School.fromJson(Map<String, dynamic> json) {
    return School(
      id: json['id'] ?? json['_id'] ?? '',
      nom: json['nom'] ?? '',
      region: json['region'] ?? '',
      ville: json['ville'] ?? '',
      regionDisplay: json['region_display'] ?? json['region'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nom': nom,
      'region': region,
      'ville': ville,
    };
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is School && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;
}
