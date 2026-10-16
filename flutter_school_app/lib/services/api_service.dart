import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/school.dart';
import '../models/teacher.dart';
import '../models/room.dart';
import '../models/school_class.dart';
import '../models/matiere.dart';

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000/api';

  // Dashboard Stats
  static Future<Map<String, int>> getDashboardStats() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/dashboard/'));
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        return {
          'schools_count': data['schools_count'] ?? 0,
          'matieres_count': data['matieres_count'] ?? 0,
          'teachers_count': data['teachers_count'] ?? 0,
          'rooms_count': data['rooms_count'] ?? 0,
          'classes_count': data['classes_count'] ?? 0,
        };
      }
    } catch (_) {}
    return {'schools_count': 0, 'matieres_count': 0, 'teachers_count': 0, 'rooms_count': 0, 'classes_count': 0};
  }

  // Auth
  static Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'status': 'error', 'message': e.toString()};
    }
  }

  static Future<Map<String, dynamic>> signup(String username, String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/signup/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'email': email, 'password': password}),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {'status': 'error', 'message': e.toString()};
    }
  }

  // Metadata – Matières
  static Future<List<Matiere>> getMatieres() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/matieres/'));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => Matiere.fromJson(json as Map<String, dynamic>)).toList();
      }
    } catch (_) {}
    return [];
  }

  static Future<bool> addMatiere(String nom, List<String> niveaux, int volumeHoraire) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/matieres/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'nom': nom, 'niveaux': niveaux, 'volume_horaire': volumeHoraire}),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<bool> updateMatiere(String matiereId, String nom, List<String> niveaux, int volumeHoraire) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/matieres/$matiereId/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'nom': nom, 'niveaux': niveaux, 'volume_horaire': volumeHoraire}),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<bool> deleteMatiere(String matiereId) async {
    try {
      final response = await http.delete(Uri.parse('$baseUrl/matieres/$matiereId/'));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<List<Map<String, String>>> getGouvernorats() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/gouvernorats/'));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((e) => {'code': e['code'].toString(), 'label': e['label'].toString()}).toList();
      }
    } catch (_) {}
    return [
      {'code': 'tunis', 'label': 'Tunis'},
      {'code': 'ariana', 'label': 'Ariana'},
      {'code': 'ben_arous', 'label': 'Ben Arous'},
      {'code': 'manouba', 'label': 'Manouba'},
      {'code': 'nabeul', 'label': 'Nabeul'},
      {'code': 'zaghouan', 'label': 'Zaghouan'},
      {'code': 'bizerte', 'label': 'Bizerte'},
      {'code': 'beja', 'label': 'Béja'},
      {'code': 'jendouba', 'label': 'Jendouba'},
      {'code': 'kef', 'label': 'Le Kef'},
      {'code': 'siliana', 'label': 'Siliana'},
      {'code': 'sousse', 'label': 'Sousse'},
      {'code': 'monastir', 'label': 'Monastir'},
      {'code': 'mahdia', 'label': 'Mahdia'},
      {'code': 'sfax', 'label': 'Sfax'},
      {'code': 'kairouan', 'label': 'Kairouan'},
      {'code': 'kasserine', 'label': 'Kasserine'},
      {'code': 'sidi_bouzid', 'label': 'Sidi Bouzid'},
      {'code': 'gabes', 'label': 'Gabès'},
      {'code': 'medenine', 'label': 'Médenine'},
      {'code': 'tataouine', 'label': 'Tataouine'},
      {'code': 'gafsa', 'label': 'Gafsa'},
      {'code': 'tozeur', 'label': 'Tozeur'},
      {'code': 'kebili', 'label': 'Kébili'},
    ];
  }

  // 1. Écoles
  static Future<List<School>> getSchools() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/schools/'));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => School.fromJson(json)).toList();
      }
    } catch (_) {}
    return [];
  }

  static Future<bool> addSchool(String nom, String region, String ville) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/schools/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'nom': nom, 'region': region, 'ville': ville}),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<bool> deleteSchool(String schoolId) async {
    try {
      final response = await http.delete(Uri.parse('$baseUrl/schools/$schoolId/'));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // 2. Enseignants
  static Future<List<Teacher>> getTeachers(String schoolId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/schools/$schoolId/teachers/'));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => Teacher.fromJson(json)).toList();
      }
    } catch (_) {}
    return [];
  }

  static Future<bool> addTeacher(String schoolId, String nom, String niveaux, int volumeHoraire, String scheduleText) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/schools/$schoolId/teachers/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'nom': nom,
          'niveaux': niveaux,
          'volume_horaire': volumeHoraire,
          'schedule_text': scheduleText.isNotEmpty ? scheduleText : 'Non renseigné',
        }),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<bool> deleteTeacher(String teacherId) async {
    try {
      final response = await http.delete(Uri.parse('$baseUrl/teachers/$teacherId/'));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<bool> claimAbsence(String teacherId, String reason, String dateStart, String dateEnd) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/teachers/$teacherId/claim/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'reason': reason,
          'date_start': dateStart,
          'date_end': dateEnd,
        }),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // 3. Salles
  static Future<List<Room>> getRooms(String schoolId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/schools/$schoolId/rooms/'));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => Room.fromJson(json)).toList();
      }
    } catch (_) {}
    return [];
  }

  static Future<bool> addRoom(String schoolId, String numero, String type, int capacite) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/schools/$schoolId/rooms/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'numero': numero, 'type': type, 'capacite': capacite}),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<bool> deleteRoom(String roomId) async {
    try {
      final response = await http.delete(Uri.parse('$baseUrl/rooms/$roomId/'));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<bool> toggleRoomBreakdown(String roomId, String duration) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/rooms/$roomId/breakdown/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'broken_duration': duration}),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // 4. Classes
  static Future<List<SchoolClass>> getClasses(String schoolId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/schools/$schoolId/classes/'));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => SchoolClass.fromJson(json)).toList();
      }
    } catch (_) {}
    return [];
  }

  static Future<bool> addClass(String schoolId, String nomClasse, int niveau) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/schools/$schoolId/classes/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'nom': nomClasse, 'niveau': niveau}),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<bool> deleteClass(String classId) async {
    try {
      final response = await http.delete(Uri.parse('$baseUrl/classes/$classId/'));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<bool> updateClassSchedule(String classId, String scheduleDetails) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/classes/$classId/update-schedule/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'schedule_details': scheduleDetails}),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}

