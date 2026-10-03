class Lead {
  final String name;
  final String mobile;
  final String email;
  final String project;
  final String source;
  final String status;
  final DateTime createdDate;

  Lead({
    required this.name,
    required this.mobile,
    required this.email,
    required this.project,
    required this.source,
    required this.status,
    required this.createdDate,
  });
}

final List<Lead> sampleLeads = [
  Lead(
    name: 'Rajesh Patel',
    mobile: '9876543210',
    email: 'rajesh@example.com',
    project: 'Hillcrest',
    source: 'Facebook',
    status: 'New',
    createdDate: DateTime(2026, 8, 14),
  ),

  Lead(
    name: 'Amit Shah',
    mobile: '9876501234',
    email: 'amit@example.com',
    project: 'Amara',
    source: 'Instagram',
    status: 'Contacted',
    createdDate: DateTime(2026, 8, 13),
  ),

  Lead(
    name: 'Neha Mehta',
    mobile: '9876512345',
    email: 'neha@example.com',
    project: 'Enchante',
    source: 'Website',
    status: 'New',
    createdDate: DateTime(2026, 8, 10),
  ),

  Lead(
    name: 'Karan Joshi',
    mobile: '9876523456',
    email: 'karan@example.com',
    project: 'Pacifica One',
    source: 'Facebook',
    status: 'Interested',
    createdDate: DateTime(2026, 8, 5),
  ),

  Lead(
    name: 'Pooja Desai',
    mobile: '9876534567',
    email: 'pooja@example.com',
    project: 'Hillcrest',
    source: 'Website',
    status: 'Converted',
    createdDate: DateTime(2026, 7, 28),
  ),
];