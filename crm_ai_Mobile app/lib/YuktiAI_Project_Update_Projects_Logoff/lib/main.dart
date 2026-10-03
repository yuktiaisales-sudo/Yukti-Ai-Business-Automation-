import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const YuktiAIApp());
}

class YuktiAIApp extends StatelessWidget {
  const YuktiAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Yukti-AI Business Automation',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF6F7FB),
        fontFamily: 'Arial',
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF3157D5),
        ),
      ),
      home: const CrmUrlScreen(),
      routes: {
        '/crm-url': (_) => const CrmUrlScreen(),
      },
    );
  }
}

class CrmUrlScreen extends StatefulWidget {
  const CrmUrlScreen({super.key});

  @override
  State<CrmUrlScreen> createState() => _CrmUrlScreenState();
}

class _CrmUrlScreenState extends State<CrmUrlScreen> {
  final controller = TextEditingController();

  void _go() {
    final value = controller.text.trim();
    if (value.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter your CRM URL.')),
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => CrmLoginScreen(crmUrl: value),
      ),
    );
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(26, 30, 26, 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 30),
              Row(
                children: [
                  Container(
                    width: 52,
                    height: 52,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(16),
                      gradient: const LinearGradient(
                        colors: [Color(0xFF3157D5), Color(0xFF6A4CE8)],
                      ),
                    ),
                    child: const Center(
                      child: Text(
                        'Y',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 27,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 14),
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'YUKTI-AI',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      Text(
                        'Business Automation',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 62),
              const Text(
                'Connect your CRM',
                style: TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                'Enter the CRM address you use on your laptop or PC.',
                style: TextStyle(
                  fontSize: 15,
                  height: 1.5,
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(height: 30),
              const Text(
                'CRM URL',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 9),
              TextField(
                controller: controller,
                keyboardType: TextInputType.url,
                textInputAction: TextInputAction.go,
                onSubmitted: (_) => _go(),
                decoration: InputDecoration(
                  hintText: 'https://your-crm.com',
                  prefixIcon: const Icon(Icons.language_rounded),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide.none,
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(color: Colors.grey.shade200),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(
                      color: Color(0xFF3157D5),
                      width: 1.5,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 18),
              SizedBox(
                height: 56,
                child: FilledButton(
                  onPressed: _go,
                  style: FilledButton.styleFrom(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'GO',
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      SizedBox(width: 9),
                      Icon(Icons.arrow_forward_rounded),
                    ],
                  ),
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.lock_outline_rounded),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'CRM credentials are requested only after the CRM URL step.',
                        style: TextStyle(fontSize: 12.5, height: 1.45),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              Center(
                child: Text(
                  'YUKTI-AI  •  Business Automation',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: Colors.grey,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class CrmLoginScreen extends StatefulWidget {
  final String crmUrl;

  const CrmLoginScreen({super.key, required this.crmUrl});

  @override
  State<CrmLoginScreen> createState() => _CrmLoginScreenState();
}

class _CrmLoginScreenState extends State<CrmLoginScreen> {
  final username = TextEditingController();
  final password = TextEditingController();
  bool obscure = true;
  bool connecting = false;

  Future<void> _connect() async {
    if (username.text.trim().isEmpty || password.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter username and password.')),
      );
      return;
    }

    setState(() => connecting = true);
    await Future.delayed(const Duration(milliseconds: 600));

    if (!mounted) return;

    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(
        builder: (_) => DashboardScreen(crmUrl: widget.crmUrl),
      ),
      (_) => false,
    );
  }

  @override
  void dispose() {
    username.dispose();
    password.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'CRM Login',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        backgroundColor: Colors.transparent,
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(26, 20, 26, 30),
        children: [
          Container(
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.grey.shade200),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.link_rounded,
                  color: Color(0xFF3157D5),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    widget.crmUrl,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 12.5,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 30),
          const Text(
            'Sign in to your CRM',
            style: TextStyle(
              fontSize: 29,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 9),
          Text(
            'Use the same CRM username and password you use on your computer.',
            style: TextStyle(
              color: Colors.grey.shade600,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 28),
          const Text(
            'Username',
            style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: username,
            textInputAction: TextInputAction.next,
            decoration: InputDecoration(
              hintText: 'Enter CRM username',
              prefixIcon: const Icon(Icons.person_outline_rounded),
              filled: true,
              fillColor: Colors.white,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
          ),
          const SizedBox(height: 18),
          const Text(
            'Password',
            style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: password,
            obscureText: obscure,
            textInputAction: TextInputAction.done,
            onSubmitted: (_) => _connect(),
            decoration: InputDecoration(
              hintText: 'Enter CRM password',
              prefixIcon: const Icon(Icons.lock_outline_rounded),
              suffixIcon: IconButton(
                onPressed: () => setState(() => obscure = !obscure),
                icon: Icon(
                  obscure
                      ? Icons.visibility_outlined
                      : Icons.visibility_off_outlined,
                ),
              ),
              filled: true,
              fillColor: Colors.white,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
          ),
          const SizedBox(height: 24),
          SizedBox(
            height: 56,
            child: FilledButton(
              onPressed: connecting ? null : _connect,
              style: FilledButton.styleFrom(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
              child: connecting
                  ? const SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.4,
                        color: Colors.white,
                      ),
                    )
                  : const Text(
                      'CONNECT TO CRM',
                      style: TextStyle(fontWeight: FontWeight.w800),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  final String? crmUrl;

  const DashboardScreen({super.key, this.crmUrl});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  String selectedPeriod = 'This Month';
  String selectedProject = 'All';

  int totalLeads = 0;
  int todayLeads = 0;

  bool isLoading = false;
  bool isConnected = false;

  int currentIndex = 0;

  final periods = ['Today', 'This Week', 'This Month', 'Last Month'];
  final projects = ['All', 'Pride Towers', 'San Lucas', 'San Martin'];

  @override
  void initState() {
    super.initState();
    fetchData();
  }

  Future<void> fetchData() async {
    setState(() => isLoading = true);

    try {
      final uri = Uri.parse(
        'http://127.0.0.1:5050/api/data'
        '?month=${Uri.encodeComponent(selectedPeriod)}'
        '&project=${Uri.encodeComponent(selectedProject)}',
      );

      final response =
          await http.get(uri).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        if (!mounted) return;
        setState(() {
          totalLeads = _toInt(data['total_leads']);
          todayLeads = _toInt(data['today_leads']);
          isConnected = true;
          isLoading = false;
        });
      } else {
        throw Exception('Server returned ${response.statusCode}');
      }
    } catch (_) {
      if (!mounted) return;
      setState(() {
        isConnected = false;
        isLoading = false;
      });
    }
  }

  Future<void> _logOff() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text(
          'Log Off?',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        content: const Text(
          'You will be returned to the CRM connection screen.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Log Off'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    Navigator.of(context).pushNamedAndRemoveUntil(
      '/crm-url',
      (route) => false,
    );
  }

  int _toInt(dynamic value) =>
      value is int ? value : int.tryParse('$value') ?? 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: IndexedStack(
          index: currentIndex,
          children: [
            _dashboard(),
            _placeholder('Leads', Icons.groups_rounded,
                'Manage and monitor your business leads.'),
            _placeholder('Automations', Icons.smart_toy_rounded,
                'Monitor your Yukti-AI business workflows.'),
            _placeholder('Reports', Icons.bar_chart_rounded,
                'Business performance and automation reports.'),
            _placeholder('Settings', Icons.settings_rounded,
                'Manage your Yukti-AI business environment.'),
          ],
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: currentIndex,
        onDestinationSelected: (i) => setState(() => currentIndex = i),
        height: 72,
        destinations: const [
          NavigationDestination(
              icon: Icon(Icons.home_outlined),
              selectedIcon: Icon(Icons.home_rounded),
              label: 'Home'),
          NavigationDestination(
              icon: Icon(Icons.groups_outlined),
              selectedIcon: Icon(Icons.groups_rounded),
              label: 'Leads'),
          NavigationDestination(
              icon: Icon(Icons.smart_toy_outlined),
              selectedIcon: Icon(Icons.smart_toy_rounded),
              label: 'Automation'),
          NavigationDestination(
              icon: Icon(Icons.bar_chart_outlined),
              selectedIcon: Icon(Icons.bar_chart_rounded),
              label: 'Reports'),
          NavigationDestination(
              icon: Icon(Icons.settings_outlined),
              selectedIcon: Icon(Icons.settings_rounded),
              label: 'Settings'),
        ],
      ),
    );
  }

  Widget _dashboard() {
    return RefreshIndicator(
      onRefresh: fetchData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(20, 18, 20, 30),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _header(),
            const SizedBox(height: 18),
            _connection(),
            const SizedBox(height: 18),
            Row(
              children: [
                Expanded(
                  child: _filter(
                    'PERIOD',
                    selectedPeriod,
                    periods,
                    Icons.calendar_today_outlined,
                    (v) {
                      if (v == null) return;
                      setState(() => selectedPeriod = v);
                      fetchData();
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _filter(
                    'PROJECT',
                    selectedProject,
                    projects,
                    Icons.business_outlined,
                    (v) {
                      if (v == null) return;
                      setState(() => selectedProject = v);
                      fetchData();
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 22),
            const Text(
              'Business Overview',
              style: TextStyle(
                fontSize: 25,
                fontWeight: FontWeight.w800,
                color: Color(0xFF20232D),
              ),
            ),
            const SizedBox(height: 5),
            const Text(
              'Monitor your business performance and automation health.',
              style: TextStyle(fontSize: 13, color: Color(0xFF777B87)),
            ),
            const SizedBox(height: 18),
            Row(
              children: [
                Expanded(
                  child: _kpi(
                    'TOTAL LEADS',
                    '$totalLeads',
                    selectedPeriod,
                    Icons.groups_rounded,
                  ),
                ),
                const SizedBox(width: 13),
                Expanded(
                  child: _kpi(
                    "TODAY'S LEADS",
                    '$todayLeads',
                    'Today',
                    Icons.trending_up_rounded,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 22),
            _section(
              'Lead Performance',
              'Lead activity overview',
              Icons.analytics_outlined,
              SizedBox(
                height: 150,
                child: CustomPaint(
                  painter: _ChartPainter(),
                  child: const SizedBox.expand(),
                ),
              ),
            ),
            const SizedBox(height: 22),
            _section(
              'Project Performance',
              'Leads by project',
              Icons.business_outlined,
              Column(
                children: [
                  _project('Pride Towers', .82, totalLeads),
                  _project('San Lucas', .65, 0),
                  _project('San Martin', .48, 0),
                ],
              ),
            ),
            const SizedBox(height: 22),
            _section(
              'Automation Health',
              'Your automation environment',
              Icons.smart_toy_outlined,
              Column(
                children: [
                  _status('Outlook Lead Reader', 'Healthy'),
                  _status('Excel / Master File', 'Healthy'),
                  _status('CRM Upload', 'Healthy'),
                  _status('Power BI', 'Connected'),
                ],
              ),
            ),
            const SizedBox(height: 22),
            _section(
              "Today's Activity",
              'Latest business automation activity',
              Icons.history_rounded,
              Column(
                children: [
                  _activity('Marketing Leads', 'Automation ready'),
                  _activity('CRM Upload', 'System monitoring active'),
                  _activity('Dashboard', 'Data synchronized'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _header() => Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(15),
              gradient: const LinearGradient(
                colors: [Color(0xFF3157D5), Color(0xFF6A4CE8)],
              ),
            ),
            child: const Center(
              child: Text('Y',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 25,
                      fontWeight: FontWeight.w800)),
            ),
          ),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('YUKTI-AI',
                    style: TextStyle(
                        fontSize: 20, fontWeight: FontWeight.w800)),
                Text('Business Automation',
                    style: TextStyle(
                        fontSize: 12, color: Color(0xFF777B87))),
              ],
            ),
          ),
          IconButton(
            onPressed: () {},
            icon: const Icon(Icons.notifications_none_rounded),
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'logout') {
                _logOff();
              }
            },
            itemBuilder: (context) => const [
              PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(Icons.logout_rounded),
                    SizedBox(width: 10),
                    Text('Log Off'),
                  ],
                ),
              ),
            ],
            icon: const Icon(Icons.person_outline_rounded),
          ),
        ],
      );

  Widget _connection() => Container(
        padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 11),
        decoration: BoxDecoration(
          color: isConnected
              ? const Color(0xFFEAF8F0)
              : const Color(0xFFFFF4E5),
          borderRadius: BorderRadius.circular(15),
        ),
        child: Row(
          children: [
            Icon(
              Icons.circle,
              size: 10,
              color: isConnected
                  ? const Color(0xFF22A861)
                  : const Color(0xFFE99A2E),
            ),
            const SizedBox(width: 9),
            Expanded(
              child: Text(
                isConnected
                    ? (widget.crmUrl == null
                        ? 'CRM Connected'
                        : 'CRM Connected • ${widget.crmUrl}')
                    : 'CRM Connection Unavailable',
                style: TextStyle(
                  fontWeight: FontWeight.w700,
                  color: isConnected
                      ? const Color(0xFF187847)
                      : const Color(0xFF9A641C),
                ),
              ),
            ),
            if (isLoading)
              const SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            else
              IconButton(
                visualDensity: VisualDensity.compact,
                onPressed: fetchData,
                icon: const Icon(Icons.refresh_rounded),
              ),
          ],
        ),
      );

  Widget _filter(
    String label,
    String value,
    List<String> items,
    IconData icon,
    ValueChanged<String?> onChanged,
  ) =>
      Container(
        padding: const EdgeInsets.fromLTRB(12, 8, 7, 4),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(15),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 12, color: const Color(0xFF737784)),
                const SizedBox(width: 5),
                Text(label,
                    style: const TextStyle(
                        fontSize: 9,
                        fontWeight: FontWeight.w800,
                        letterSpacing: .7,
                        color: Color(0xFF898D98))),
              ],
            ),
            DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: value,
                isExpanded: true,
                icon: const Icon(Icons.keyboard_arrow_down_rounded),
                style: const TextStyle(
                    color: Color(0xFF252833),
                    fontSize: 13,
                    fontWeight: FontWeight.w700),
                items: items
                    .map((e) =>
                        DropdownMenuItem(value: e, child: Text(e)))
                    .toList(),
                onChanged: onChanged,
              ),
            ),
          ],
        ),
      );

  Widget _kpi(String title, String value, String subtitle, IconData icon) =>
      Container(
        padding: const EdgeInsets.all(17),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              blurRadius: 24,
              offset: const Offset(0, 7),
              color: Colors.black.withValues(alpha: .04),
            )
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: const Color(0xFF3157D5), size: 25),
            const SizedBox(height: 15),
            Text(title,
                style: const TextStyle(
                    fontSize: 10,
                    letterSpacing: .7,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF888C97))),
            const SizedBox(height: 4),
            Text(value,
                style: const TextStyle(
                    fontSize: 28, fontWeight: FontWeight.w800)),
            const SizedBox(height: 3),
            Text(subtitle,
                style: const TextStyle(
                    fontSize: 11, color: Color(0xFF9295A0))),
          ],
        ),
      );

  Widget _section(String title, String subtitle, IconData icon, Widget child) =>
      Container(
        width: double.infinity,
        padding: const EdgeInsets.fromLTRB(17, 17, 17, 18),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              blurRadius: 25,
              offset: const Offset(0, 7),
              color: Colors.black.withValues(alpha: .04),
            )
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title,
                          style: const TextStyle(
                              fontSize: 16, fontWeight: FontWeight.w800)),
                      const SizedBox(height: 3),
                      Text(subtitle,
                          style: const TextStyle(
                              fontSize: 11, color: Color(0xFF9497A1))),
                    ],
                  ),
                ),
                Icon(icon, color: const Color(0xFF3157D5)),
              ],
            ),
            const SizedBox(height: 5),
            child,
          ],
        ),
      );

  Widget _project(String name, double progress, int value) => Padding(
        padding: const EdgeInsets.only(top: 14),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                    child: Text(name,
                        style: const TextStyle(
                            fontSize: 13, fontWeight: FontWeight.w700))),
                Text(value == 0 ? '--' : '$value',
                    style: const TextStyle(fontWeight: FontWeight.w800)),
              ],
            ),
            const SizedBox(height: 8),
            ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: LinearProgressIndicator(
                value: progress,
                minHeight: 7,
                backgroundColor: const Color(0xFFEEF0F5),
              ),
            ),
          ],
        ),
      );

  Widget _status(String title, String status) => Padding(
        padding: const EdgeInsets.only(top: 14),
        child: Row(
          children: [
            const Icon(Icons.check_circle_rounded,
                size: 19, color: Color(0xFF22A861)),
            const SizedBox(width: 10),
            Expanded(
              child: Text(title,
                  style: const TextStyle(
                      fontSize: 13, fontWeight: FontWeight.w700)),
            ),
            Text(status,
                style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF21844E))),
          ],
        ),
      );

  Widget _activity(String title, String subtitle) => Padding(
        padding: const EdgeInsets.only(top: 14),
        child: Row(
          children: [
            const Icon(Icons.check_circle_outline_rounded,
                color: Color(0xFF3157D5)),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: const TextStyle(
                          fontSize: 13, fontWeight: FontWeight.w700)),
                  Text(subtitle,
                      style: const TextStyle(
                          fontSize: 11, color: Color(0xFF9295A0))),
                ],
              ),
            ),
          ],
        ),
      );

  Widget _placeholder(String title, IconData icon, String subtitle) =>
      SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, size: 45, color: const Color(0xFF3157D5)),
            const SizedBox(height: 15),
            Text(title,
                style: const TextStyle(
                    fontSize: 28, fontWeight: FontWeight.w800)),
            const SizedBox(height: 5),
            Text(subtitle,
                style: const TextStyle(
                    fontSize: 13, color: Color(0xFF777B87))),
            const SizedBox(height: 25),
            const Card(
              child: Padding(
                padding: EdgeInsets.all(20),
                child: Text(
                  'This section is part of the Yukti-AI global platform and will be connected in the next development stage.',
                ),
              ),
            ),
          ],
        ),
      );
}

class _ChartPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final grid = Paint()
      ..color = const Color(0xFFEDEFF4)
      ..strokeWidth = 1;

    final line = Paint()
      ..color = const Color(0xFF3157D5)
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    for (int i = 1; i <= 4; i++) {
      final y = size.height * i / 5;
      canvas.drawLine(Offset(0, y), Offset(size.width, y), grid);
    }

    final points = [
      Offset(0, size.height * .68),
      Offset(size.width * .16, size.height * .57),
      Offset(size.width * .33, size.height * .62),
      Offset(size.width * .50, size.height * .35),
      Offset(size.width * .67, size.height * .48),
      Offset(size.width * .83, size.height * .23),
      Offset(size.width, size.height * .30),
    ];

    final path = Path()..moveTo(points.first.dx, points.first.dy);
    for (final p in points.skip(1)) {
      path.lineTo(p.dx, p.dy);
    }
    canvas.drawPath(path, line);

    final dot = Paint()..color = const Color(0xFF3157D5);
    for (final p in points) {
      canvas.drawCircle(p, 4, dot);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
