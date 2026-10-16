import os

# teachers/list.html
with open('templates/teachers/list.html', 'r', encoding='utf-8') as f:
    content = f.read()
target = """                            <button class="btn btn-outline-warning text-dark" data-bs-toggle="modal" data-bs-target="#claimModal{{ teacher.id }}">
                                Réclamation d'absence
                            </button>
                        </div>"""
replacement = """                            <button class="btn btn-outline-warning text-dark" data-bs-toggle="modal" data-bs-target="#claimModal{{ teacher.id }}">
                                Réclamation d'absence
                            </button>
                        </div>
                        <div class="btn-group btn-group-sm ms-2">
                            <a href="{% url 'teacher_edit' teacher.id %}" class="btn btn-outline-primary" title="Éditer">✏️</a>
                            <a href="{% url 'teacher_delete' teacher.id %}" class="btn btn-outline-danger" title="Supprimer" onclick="return confirm('Supprimer cet enseignant ?');">🗑️</a>
                        </div>"""
content = content.replace(target, replacement, 1)
with open('templates/teachers/list.html', 'w', encoding='utf-8') as f:
    f.write(content)

# rooms/list.html
with open('templates/rooms/list.html', 'r', encoding='utf-8') as f:
    content = f.read()
target2 = """                            <button class="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#panneModal{{ room.id }}">
                                {% if room.is_broken %}
                                En réparation
                                {% else %}
                                En panne
                                {% endif %}
                            </button>
                        </div>"""
# The text in rooms/list is slightly different, wait let's check what it actually is via a simpler replace
import re
content = re.sub(r'(</button>\s*</div>)\s*(?=<!-- (Schedule|Absence|Panne) Edit/View Modal -->|<div class="modal fade" id="scheduleModal)', r'\1\n                        <div class="btn-group btn-group-sm ms-2">\n                            <a href="{% url \'room_edit\' room.id %}" class="btn btn-outline-primary" title="Éditer">✏️</a>\n                            <a href="{% url \'room_delete\' room.id %}" class="btn btn-outline-danger" title="Supprimer" onclick="return confirm(\'Supprimer cette salle ?\');">🗑️</a>\n                        </div>\n', content, count=1)
# Actually, I'll just use a generalized regex for rooms/list.html
# Let's write specifically for rooms/list.html
content_rooms = ""
with open('templates/rooms/list.html', 'r', encoding='utf-8') as f:
    content_rooms = f.read()

# find `<div class="btn-group btn-group-sm">` and its closing `</div>`, insert the new div after it
content_rooms = re.sub(
    r'(<div class="btn-group btn-group-sm">[\s\S]*?</div>)',
    r'\1\n                        <div class="btn-group btn-group-sm ms-2">\n                            <a href="{% url \'room_edit\' room.id %}" class="btn btn-outline-primary" title="Éditer">✏️</a>\n                            <a href="{% url \'room_delete\' room.id %}" class="btn btn-outline-danger" title="Supprimer" onclick="return confirm(\'Supprimer cette salle ?\');">🗑️</a>\n                        </div>',
    content_rooms
)
with open('templates/rooms/list.html', 'w', encoding='utf-8') as f:
    f.write(content_rooms)


# classes/list.html
content_classes = ""
with open('templates/classes/list.html', 'r', encoding='utf-8') as f:
    content_classes = f.read()

content_classes = re.sub(
    r'(<button class="btn btn-outline-primary" data-bs-toggle="modal" data-bs-target="#scheduleModal{{ class\.id }}">[\s\S]*?</button>\s*</div>)',
    r'\1\n                        <div class="btn-group btn-group-sm ms-2">\n                            <a href="{% url \'class_edit\' class.id %}" class="btn btn-outline-secondary" title="Éditer">✏️</a>\n                            <a href="{% url \'class_delete\' class.id %}" class="btn btn-outline-danger" title="Supprimer" onclick="return confirm(\'Supprimer cette classe ?\');">🗑️</a>\n                        </div>',
    content_classes
)
with open('templates/classes/list.html', 'w', encoding='utf-8') as f:
    f.write(content_classes)

