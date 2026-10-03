import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:excel/excel.dart' as excel;
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:share_plus/share_plus.dart';
import 'package:http/http.dart' as http;
import 'package:qr_flutter/qr_flutter.dart';

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
    );
  }
}

// ============================================================
// YUKTI-AI BRANDING
// ============================================================
class YuktiBrandLogo extends StatelessWidget {
  final double height;
  final bool iconOnly;

  const YuktiBrandLogo({super.key, this.height = 70, this.iconOnly = false});

  @override
  Widget build(BuildContext context) {
    if (iconOnly) {
      return Image.asset(
        'assets/images/yukti_ai_app_icon.png',
        width: height,
        height: height,
        fit: BoxFit.contain,
      );
    }
    return Image.asset(
      'assets/images/yukti_ai_business_automation_logo.png',
      height: height,
      fit: BoxFit.contain,
    );
  }
}

// ============================================================
// CRM CONNECTION - URL VALIDATION
// ============================================================
class CrmConnectionService {
  static Future<CrmUrlResult> validateUrl(String value) async {
    var text = value.trim();

    if (text.isEmpty) {
      return const CrmUrlResult(false, 'Please enter your CRM URL.');
    }

    if (!text.startsWith('http://') && !text.startsWith('https://')) {
      text = 'https://$text';
    }

    final uri = Uri.tryParse(text);

    if (uri == null || uri.host.isEmpty) {
      return const CrmUrlResult(false, 'Please enter a valid CRM URL.');
    }

    // We validate the URL and try to reach it. Some CRMs reject automated
    // requests, so a network rejection does not automatically mean the URL
    // is invalid.
    try {
      final response = await http.get(uri).timeout(
        const Duration(seconds: 8),
      );

      if (response.statusCode >= 200 && response.statusCode < 500) {
        return CrmUrlResult(
          true,
          'CRM URL is reachable.',
          normalizedUrl: uri.toString(),
        );
      }
    } catch (_) {}

    return CrmUrlResult(
      true,
      'CRM URL format is valid. Continue with login.',
      normalizedUrl: uri.toString(),
    );
  }
}

class CrmUrlResult {
  final bool success;
  final String message;
  final String? normalizedUrl;

  const CrmUrlResult(
    this.success,
    this.message, {
    this.normalizedUrl,
  });
}


// ============================================================
// SCREEN 1 - CRM URL
// ============================================================

class CrmUrlScreen extends StatefulWidget {
  const CrmUrlScreen({super.key});

  @override
  State<CrmUrlScreen> createState() => _CrmUrlScreenState();
}

class _CrmUrlScreenState extends State<CrmUrlScreen> {
  final _urlController = TextEditingController();
  bool _checking = false;
  String? _error;

  Future<void> _go() async {
    FocusScope.of(context).unfocus();

    setState(() {
      _checking = true;
      _error = null;
    });

    final result = await CrmConnectionService.validateUrl(
      _urlController.text,
    );

    if (!mounted) return;

    setState(() => _checking = false);

    if (!result.success) {
      setState(() => _error = result.message);
      return;
    }

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => CrmLoginScreen(
          crmUrl: result.normalizedUrl ?? _urlController.text.trim(),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(26, 24, 26, 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 30),
              Center(
                child: YuktiBrandLogo(height: 155),
              ),
              const SizedBox(height: 62),
              const Text(
                'Connect your CRM',
                style: TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.w800,
                  letterSpacing: -0.8,
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
                controller: _urlController,
                keyboardType: TextInputType.url,
                textInputAction: TextInputAction.go,
                onSubmitted: (_) => _go(),
                decoration: InputDecoration(
                  hintText: 'https://your-crm.com',
                  prefixIcon: const Icon(Icons.language_rounded),
                  errorText: _error,
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
                  onPressed: _checking ? null : _go,
                  style: FilledButton.styleFrom(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: _checking
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.4,
                            color: Colors.white,
                          ),
                        )
                      : const Row(
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
                child: Row(
                  children: [
                    Icon(
                      Icons.lock_outline_rounded,
                      color: Colors.grey.shade700,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Your CRM credentials will be requested only after this CRM URL step.',
                        style: TextStyle(
                          fontSize: 12.5,
                          height: 1.45,
                          color: Colors.grey.shade700,
                        ),
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
                    color: Colors.grey.shade500,
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


// ============================================================
// SCREEN 2 - CRM LOGIN
// ============================================================

class CrmLoginScreen extends StatefulWidget {
  final String crmUrl;

  const CrmLoginScreen({
    super.key,
    required this.crmUrl,
  });

  @override
  State<CrmLoginScreen> createState() => _CrmLoginScreenState();
}

class _CrmLoginScreenState extends State<CrmLoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();

  bool _obscure = true;
  bool _connecting = false;

  // Inline login 2FA state.
  bool _show2FA = false;
  bool _verifying2FA = false;
  bool _sendingLoginOtp = false;
  bool _loginOtpSent = false;
  String _twoFactorMethod = 'authenticator';
  String? _twoFactorAccountId;
  String? _registeredEmail;
  String? _loginOtpRequestId;
  String? _twoFactorError;
  final _twoFactorCodeController = TextEditingController();

  Future<void> _openDashboard() async {
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const DashboardScreen()),
      (route) => false,
    );
  }

  Future<void> _connect() async {
    FocusScope.of(context).unfocus();

    final username = _usernameController.text.trim();
    final password = _passwordController.text;

    if (username.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter username and password.')),
      );
      return;
    }

    setState(() => _connecting = true);

    try {
      final response = await http.post(
        Uri.parse('${_DashboardScreenState.apiBaseUrl}/api/mobile/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);

      if (response.statusCode != 200 || data['success'] != true) {
        throw Exception(data['message'] ?? 'Invalid username or password.');
      }

      if (!mounted) return;

      setState(() => _connecting = false);

      if (data['requires_2fa'] == true) {
        setState(() {
          _twoFactorAccountId = data['account_id']?.toString() ?? 'yuktiai-mobile';
          _registeredEmail = data['registered_email']?.toString() ?? '';
          _show2FA = true;
          _twoFactorMethod = 'authenticator';
          _twoFactorCodeController.clear();
          _loginOtpSent = false;
          _loginOtpRequestId = null;
          _twoFactorError = null;
        });
        return;
      }

      await _openDashboard();
    } catch (e) {
      if (!mounted) return;
      setState(() => _connecting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _verifyAuthenticator2FA() async {
    final code = _twoFactorCodeController.text.trim();
    if (!RegExp(r'^\d{6}$').hasMatch(code)) {
      setState(() => _twoFactorError = 'Enter the 6-digit authenticator code.');
      return;
    }

    setState(() {
      _verifying2FA = true;
      _twoFactorError = null;
    });

    try {
      final response = await http.post(
        Uri.parse('${_DashboardScreenState.apiBaseUrl}/api/mobile/auth/login/2fa/totp'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'account_id': _twoFactorAccountId,
          'code': code,
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      if (response.statusCode != 200 || data['success'] != true) {
        throw Exception(data['message'] ?? 'Authenticator verification failed.');
      }

      await _openDashboard();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _verifying2FA = false;
        _twoFactorError = e.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  Future<void> _sendLoginOtp() async {
    if ((_registeredEmail ?? '').isEmpty) {
      setState(() => _twoFactorError = 'No registered email is configured for this account.');
      return;
    }

    setState(() {
      _sendingLoginOtp = true;
      _twoFactorError = null;
    });

    try {
      final response = await http.post(
        Uri.parse('${_DashboardScreenState.apiBaseUrl}/api/mobile/auth/login/2fa/email/request'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'account_id': _twoFactorAccountId}),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      if (response.statusCode != 200 || data['success'] != true) {
        throw Exception(data['message'] ?? 'Unable to send email OTP.');
      }

      if (!mounted) return;
      setState(() {
        _sendingLoginOtp = false;
        _loginOtpSent = true;
        _loginOtpRequestId = data['request_id']?.toString();
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _sendingLoginOtp = false;
        _twoFactorError = e.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  Future<void> _verifyLoginOtp() async {
    final code = _twoFactorCodeController.text.trim();
    if (_loginOtpRequestId == null || !RegExp(r'^\d{6}$').hasMatch(code)) {
      setState(() => _twoFactorError = 'Enter the 6-digit email OTP.');
      return;
    }

    setState(() {
      _verifying2FA = true;
      _twoFactorError = null;
    });

    try {
      final response = await http.post(
        Uri.parse('${_DashboardScreenState.apiBaseUrl}/api/mobile/auth/login/2fa/email/verify'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'account_id': _twoFactorAccountId,
          'request_id': _loginOtpRequestId,
          'otp': code,
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      if (response.statusCode != 200 || data['success'] != true) {
        throw Exception(data['message'] ?? 'Email OTP verification failed.');
      }

      await _openDashboard();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _verifying2FA = false;
        _twoFactorError = e.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  void _switch2FAMethod(String method) {
    setState(() {
      _twoFactorMethod = method;
      _twoFactorCodeController.clear();
      _loginOtpSent = false;
      _loginOtpRequestId = null;
      _twoFactorError = null;
    });
  }

  Widget _buildInline2FA() {
    final email = _registeredEmail ?? '';
    final maskedEmail = email.length > 4
        ? '${email.substring(0, 2)}***${email.substring(email.indexOf('@'))}'
        : email;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Two-Factor Authentication',
          style: TextStyle(fontSize: 29, fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 9),
        Text(
          'Complete one verification method to continue to the dashboard.',
          style: TextStyle(color: Colors.grey.shade600, height: 1.5),
        ),
        const SizedBox(height: 24),
        SegmentedButton<String>(
          segments: const [
            ButtonSegment(
              value: 'authenticator',
              label: Text('Authenticator'),
              icon: Icon(Icons.shield_outlined),
            ),
            ButtonSegment(
              value: 'email',
              label: Text('Email OTP'),
              icon: Icon(Icons.email_outlined),
            ),
          ],
          selected: {_twoFactorMethod},
          onSelectionChanged: _verifying2FA || _sendingLoginOtp
              ? null
              : (selection) => _switch2FAMethod(selection.first),
        ),
        const SizedBox(height: 22),
        if (_twoFactorMethod == 'authenticator') ...[
          Text(
            'Open Google Authenticator or Microsoft Authenticator and enter the current 6-digit code.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey.shade700, height: 1.45),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: _twoFactorCodeController,
            keyboardType: TextInputType.number,
            maxLength: 6,
            textAlign: TextAlign.center,
            enabled: !_verifying2FA,
            decoration: const InputDecoration(
              labelText: '6-digit authenticator code',
              hintText: '000000',
              border: OutlineInputBorder(),
            ),
          ),
        ] else ...[
          Text(
            _loginOtpSent
                ? 'OTP sent to $maskedEmail'
                : 'A 6-digit OTP will be sent to your registered email address.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey.shade700, height: 1.45),
          ),
          const SizedBox(height: 14),
          SizedBox(
            height: 50,
            child: FilledButton.icon(
              onPressed: _sendingLoginOtp || _verifying2FA ? null : _sendLoginOtp,
              icon: _sendingLoginOtp
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.send_rounded),
              label: Text(_loginOtpSent ? 'RESEND OTP' : 'SEND OTP'),
            ),
          ),
          if (_loginOtpSent) ...[
            const SizedBox(height: 14),
            TextField(
              controller: _twoFactorCodeController,
              keyboardType: TextInputType.number,
              maxLength: 6,
              textAlign: TextAlign.center,
              enabled: !_verifying2FA,
              decoration: const InputDecoration(
                labelText: '6-digit email OTP',
                hintText: '000000',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ],
        if (_twoFactorError != null) ...[
          const SizedBox(height: 8),
          Text(
            _twoFactorError!,
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.red.shade700, fontSize: 12.5),
          ),
        ],
        const SizedBox(height: 18),
        SizedBox(
          height: 56,
          child: FilledButton(
            onPressed: _verifying2FA
                ? null
                : (_twoFactorMethod == 'authenticator'
                    ? _verifyAuthenticator2FA
                    : (_loginOtpSent ? _verifyLoginOtp : null)),
            style: FilledButton.styleFrom(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            ),
            child: _verifying2FA
                ? const SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(strokeWidth: 2.4, color: Colors.white),
                  )
                : const Text(
                    'VERIFY & CONTINUE',
                    style: TextStyle(fontWeight: FontWeight.w800),
                  ),
          ),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _twoFactorCodeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Yukti-AI',
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
          if (_show2FA)
            _buildInline2FA()
          else ...[
            const Text(
              'Username',
              style: TextStyle(
                fontWeight: FontWeight.w700,
                fontSize: 13,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _usernameController,
              textInputAction: TextInputAction.next,
              decoration: InputDecoration(
                hintText: 'Enter CRM username',
                prefixIcon: const Icon(Icons.person_outline_rounded),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide(color: Colors.grey.shade200),
                ),
              ),
            ),
            const SizedBox(height: 18),
            const Text(
              'Password',
              style: TextStyle(
                fontWeight: FontWeight.w700,
                fontSize: 13,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _passwordController,
              obscureText: _obscure,
              textInputAction: TextInputAction.done,
              onSubmitted: (_) => _connect(),
              decoration: InputDecoration(
                hintText: 'Enter CRM password',
                prefixIcon: const Icon(Icons.lock_outline_rounded),
                suffixIcon: IconButton(
                  onPressed: () {
                    setState(() => _obscure = !_obscure);
                  },
                  icon: Icon(
                    _obscure
                        ? Icons.visibility_outlined
                        : Icons.visibility_off_outlined,
                  ),
                ),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide(color: Colors.grey.shade200),
                ),
              ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              height: 56,
              child: FilledButton(
                onPressed: _connecting ? null : _connect,
                style: FilledButton.styleFrom(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: _connecting
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
        ],
      ),
    );
  }
}


// ============================================================
// EXISTING YUKTI-AI HOME / DASHBOARD
// Preserved from the uploaded 20 KB+ main.dart.
// ============================================================
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  static String apiBaseUrl = 'http://172.168.1.22:5050';

  String selectedPeriod = 'This Month';
  String selectedProject = 'All';

  int totalLeads = 0;
  int todayLeads = 0;
      Map<String, int> projectCounts = {};
  String? lastSync;

  bool isLoading = false;
  bool isConnected = false;
  bool twoFactorEnabled = false;

  int currentIndex = 0;
  Timer? _syncTimer;

  final periods = ['Today', 'Yesterday', 'This Week', 'This Month', 'Last Month'];
  List<String> projects = ['All'];

  @override
  void initState() {
    super.initState();
    fetchData();
    fetchTwoFactorStatus();

    // Near-real-time polling. The existing PC backend remains the source
    // of truth; the mobile app checks for updated data every 30 seconds.
    _syncTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => fetchData(silent: true),
    );
  }

  @override
  void dispose() {
    _syncTimer?.cancel();
    super.dispose();
  }

  Future<void> fetchTwoFactorStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/api/mobile/auth/2fa/status'),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      if (response.statusCode == 200 && data['success'] == true && mounted) {
        setState(() {
          twoFactorEnabled = data['enabled'] == true;
        });
      }
    } catch (_) {
      // Keep the current UI state if the status check cannot reach the server.
    }
  }

  Future<void> fetchData({bool silent = false}) async {
    if (!silent && mounted) {
      setState(() => isLoading = true);
    }

    try {
      final uri = Uri.parse(
        '$apiBaseUrl/api/mobile/in4-data'
        '?period=${Uri.encodeComponent(selectedPeriod)}'
        '&project=${Uri.encodeComponent(selectedProject)}',
      );

      final response =
          await http.get(uri).timeout(const Duration(seconds: 10));

      if (response.statusCode != 200) {
        throw Exception('Server returned ${response.statusCode}');
      }

      final data = json.decode(response.body);

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'In4 Mobile API returned an error.');
      }

      final availableProjects = <String>['All'];
      final rawProjects = data['available_projects'];

      if (rawProjects is List) {
        for (final item in rawProjects) {
          final name = '$item'.trim();
          if (name.isNotEmpty && !availableProjects.contains(name)) {
            availableProjects.add(name);
          }
        }
      }

      // If the current selection is not present in the latest report,
      // safely return to All rather than breaking the dropdown.
      final safeSelectedProject =
          availableProjects.contains(selectedProject)
              ? selectedProject
              : 'All';

      final rawCounts = data['project_counts'];
      final counts = <String, int>{};

      if (rawCounts is Map) {
        rawCounts.forEach((key, value) {
          counts['$key'] = _toInt(value);
        });
      }

      if (!mounted) return;

      setState(() {
        totalLeads = _toInt(data['total_leads']);
        todayLeads = _toInt(data['today_leads']);
        projectCounts = counts;
        projects = availableProjects;
        selectedProject = safeSelectedProject;
        lastSync = data['last_run']?.toString();
        isConnected = data['connected'] == true;
        isLoading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        isConnected = false;
        if (!silent) isLoading = false;
      });
    }
  }

  Future<void> _logOff() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Log Off?', style: TextStyle(fontWeight: FontWeight.w800)),
        content: const Text('Are you sure you want to log off from Yukti-AI?'),
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

    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const CrmUrlScreen()),
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
            LeadsScreen(
              apiBaseUrl: apiBaseUrl,
              initialPeriod: selectedPeriod,
            ),
            AutomationScreen(
              apiBaseUrl: apiBaseUrl,
            ),
            ReportsScreen(
              apiBaseUrl: apiBaseUrl,
              initialPeriod: selectedPeriod,
            ),
            _settings(),
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

// ============================================================
// Yukti-AI Mobile App SETTINGS Tab
// ============================================================

Widget _settings() {
  return SafeArea(
    child: SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 35),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [

          // HEADER
          Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: const Color(0xFFE9EEFF),
                  borderRadius: BorderRadius.circular(15),
                ),
                child: const Icon(
                  Icons.settings_rounded,
                  color: Color(0xFF3157D5),
                  size: 27,
                ),
              ),
              const SizedBox(width: 14),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Settings',
                      style: TextStyle(
                        fontSize: 25,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    SizedBox(height: 3),
                    Text(
                      'Manage your Yukti-AI environment',
                      style: TextStyle(
                        color: Colors.grey,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // ==================================================
          // ACCOUNT
          // ==================================================
          _settingsSection(
            title: 'Account',
            subtitle: 'Account and user information',
            icon: Icons.person_outline_rounded,
            children: [
              _settingsRow(
                icon: Icons.business_outlined,
                title: 'Company',
                value: 'Not configured',
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: () => _showInfoDialog(
                  'Company',
                  'Company information will be loaded from the secure account profile after authentication is connected.',
                ),
              ),
              _settingsRow(
                icon: Icons.person_outline_rounded,
                title: 'User',
                value: 'Current logged-in user',
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: () => _showInfoDialog(
                  'User Profile',
                  'The authenticated user profile will be displayed here once the secure account service is connected.',
                ),
              ),
              _settingsRow(
                icon: Icons.badge_outlined,
                title: 'Role',
                value: 'Not configured',
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: () => _showInfoDialog(
                  'User Role',
                  'The user role and permissions will be provided by the secure account service.',
                ),
              ),
              _settingsRow(
                icon: Icons.login_rounded,
                title: 'Session',
                value: isConnected ? 'Active' : 'Not connected',
                valueColor:
                    isConnected ? Colors.green : Colors.orange,
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: () => _showInfoDialog(
                  'Session',
                  isConnected
                      ? 'The mobile application is currently connected to the Yukti-AI backend.'
                      : 'The mobile application is not currently connected to the Yukti-AI backend.',
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // ==================================================
          // CRM & API
          // ==================================================
          _settingsSection(
            title: 'CRM & API Connection',
            subtitle: 'Server and CRM connectivity',
            icon: Icons.cloud_outlined,
            children: [
              _settingsRow(
                icon: Icons.link_rounded,
                title: 'CRM URL',
                value: 'Configured at login',
                trailing: const Icon(
                  Icons.chevron_right_rounded,
                  color: Colors.grey,
                ),
                onTap: () {
                  _showInfoDialog(
                    'CRM URL',
                    'The CRM URL is configured during the CRM connection process.',
                  );
                },
              ),

              _settingsRow(
                icon: Icons.api_rounded,
                title: 'Yukti-AI API URL',
                value: apiBaseUrl,
                trailing: const Icon(
                  Icons.chevron_right_rounded,
                  color: Colors.grey,
                ),
                onTap: _showApiUrlDialog,
              ),

              _settingsRow(
                icon: Icons.wifi_rounded,
                title: 'Connection Status',
                value: isConnected ? 'Connected' : 'Disconnected',
                valueColor:
                    isConnected ? Colors.green : Colors.red,
              ),

              _settingsRow(
                icon: Icons.dns_outlined,
                title: 'Server Status',
                value: isConnected ? 'Online' : 'Unavailable',
                valueColor:
                    isConnected ? Colors.green : Colors.orange,
              ),

              _settingsRow(
                icon: Icons.sync_rounded,
                title: 'Last Sync',
                value: lastSync ?? 'Not available',
              ),

              _settingsRow(
                icon: Icons.timer_outlined,
                title: 'Auto Refresh',
                value: 'Every 30 seconds',
              ),

              const SizedBox(height: 8),

              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        fetchData();
                      },
                      icon: const Icon(Icons.sync_rounded),
                      label: const Text('SYNC NOW'),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: FilledButton.icon(
                      onPressed: () {
                        fetchData();
                      },
                      icon: const Icon(
                        Icons.network_check_rounded,
                      ),
                      label: const Text('TEST API'),
                    ),
                  ),
                ],
              ),
            ],
          ),

          const SizedBox(height: 16),

          // ==================================================
          // SECURITY
          // ==================================================
          _settingsSection(
            title: 'Security',
            subtitle: 'Authentication and account protection',
            icon: Icons.security_rounded,
            children: [
              _settingsRow(
                icon: Icons.verified_user_outlined,
                title: 'Two-Factor Authentication',
                value: twoFactorEnabled ? 'Enabled' : 'Disabled',
                valueColor: twoFactorEnabled ? Colors.green : Colors.orange,
                trailing: const Icon(
                  Icons.chevron_right_rounded,
                  color: Colors.grey,
                ),
                onTap: _showTwoFactorDialog,
              ),

              _settingsRow(
                icon: Icons.qr_code_2_rounded,
                title: 'Authenticator App',
                value: twoFactorEnabled ? 'Enabled • Google / Microsoft Authenticator' : 'Not configured',
                valueColor: twoFactorEnabled ? Colors.green : Colors.grey,
                trailing: const Icon(
                  Icons.chevron_right_rounded,
                  color: Colors.grey,
                ),
                onTap: _showAuthenticatorDialog,
              ),

              _settingsRow(
                icon: Icons.password_rounded,
                title: 'OTP Verification',
                value: 'Recovery verification method',
                trailing: const Icon(
                  Icons.chevron_right_rounded,
                  color: Colors.grey,
                ),
                onTap: _showOtpDialog,
              ),

              _settingsRow(
                icon: Icons.lock_outline_rounded,
                title: 'Change Password',
                value: 'Manage account password',
                trailing: const Icon(
                  Icons.chevron_right_rounded,
                  color: Colors.grey,
                ),
                onTap: () {
                  _showInfoDialog(
                    'Change Password',
                    'Password management will be connected to the secure Yukti-AI authentication service.',
                  );
                },
              ),

              _settingsRow(
                icon: Icons.devices_other_rounded,
                title: 'Active Session',
                value: 'Current device',
              ),

              _settingsRow(
                icon: Icons.logout_rounded,
                title: 'Log Out',
                value: 'Sign out from this device',
                trailing: const Icon(
                  Icons.chevron_right_rounded,
                  color: Colors.grey,
                ),
                onTap: _logOff,
              ),
            ],
          ),

          const SizedBox(height: 16),

          // ==================================================
          // NOTIFICATIONS
          // ==================================================
          _settingsSection(
            title: 'Notifications',
            subtitle: 'Application and automation alerts',
            icon: Icons.notifications_none_rounded,
            children: [
              _settingsRow(
                icon: Icons.smart_toy_outlined,
                title: 'Automation Alerts',
                value: 'Enabled',
                valueColor: Colors.green,
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: () => _showInfoDialog('Automation Alerts', 'Automation alerts are enabled. Notification preferences will be managed by the account notification service.'),
              ),
              _settingsRow(
                icon: Icons.cloud_upload_outlined,
                title: 'CRM Upload Alerts',
                value: 'Enabled',
                valueColor: Colors.green,
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: () => _showInfoDialog('CRM Upload Alerts', 'CRM upload alerts are enabled. Detailed delivery preferences will be managed by the notification service.'),
              ),
              _settingsRow(
                icon: Icons.error_outline_rounded,
                title: 'Error Alerts',
                value: 'Enabled',
                valueColor: Colors.green,
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: () => _showInfoDialog('Error Alerts', 'Error alerts are enabled so important automation failures can be surfaced to the user.'),
              ),
              _settingsRow(
                icon: Icons.sync_problem_outlined,
                title: 'Sync Alerts',
                value: 'Enabled',
                valueColor: Colors.green,
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: () => _showInfoDialog('Sync Alerts', 'Sync alerts are enabled for connection and synchronization events.'),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // ==================================================
          // APPLICATION
          // ==================================================
          _settingsSection(
            title: 'Application',
            subtitle: 'Yukti-AI application information',
            icon: Icons.phone_android_rounded,
            children: [
              _settingsRow(
                icon: Icons.apps_rounded,
                title: 'Application',
                value: 'Yukti-AI Business Automation',
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: () => _showInfoDialog('Application', 'Yukti-AI Business Automation mobile application.'),
              ),
              _settingsRow(
                icon: Icons.info_outline_rounded,
                title: 'App Version',
                value: 'Production version',
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: () => _showInfoDialog('App Version', 'Current production application build. The release version will be populated from the application package.'),
              ),
              _settingsRow(
                icon: Icons.api_outlined,
                title: 'API',
                value: 'Yukti-AI Secure API',
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: _showApiUrlDialog,
              ),
              _settingsRow(
                icon: Icons.cloud_done_outlined,
                title: 'Environment',
                value: isConnected ? 'Connected environment' : 'Offline / unavailable',
                valueColor: isConnected ? Colors.green : Colors.orange,
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: () => _showInfoDialog(
                  'Environment',
                  isConnected ? 'The application can currently reach the configured backend.' : 'The application cannot currently reach the configured backend.',
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // ==================================================
          // SUPPORT
          // ==================================================
          _settingsSection(
            title: 'Support & Information',
            subtitle: 'Help and legal information',
            icon: Icons.help_outline_rounded,
            children: [
              _settingsRow(
                icon: Icons.support_agent_rounded,
                title: 'Help & Support',
                value: 'Contact support',
                trailing: const Icon(
                  Icons.chevron_right_rounded,
                  color: Colors.grey,
                ),
                onTap: () {
                  _showInfoDialog(
                    'Help & Support',
                    'Yukti-AI Business Automation support information will be available here.',
                  );
                },
              ),

              _settingsRow(
                icon: Icons.privacy_tip_outlined,
                title: 'Privacy Policy',
                value: 'View privacy policy',
                trailing: const Icon(
                  Icons.chevron_right_rounded,
                  color: Colors.grey,
                ),
                onTap: () {
                  _showInfoDialog(
                    'Privacy Policy',
                    'The official Yukti-AI Privacy Policy will be connected here.',
                  );
                },
              ),

              _settingsRow(
                icon: Icons.description_outlined,
                title: 'Terms & Conditions',
                value: 'View terms',
                trailing: const Icon(
                  Icons.chevron_right_rounded,
                  color: Colors.grey,
                ),
                onTap: () {
                  _showInfoDialog(
                    'Terms & Conditions',
                    'The official Yukti-AI Terms & Conditions will be connected here.',
                  );
                },
              ),

              _settingsRow(
                icon: Icons.info_rounded,
                title: 'About Yukti-AI',
                value: 'Business Automation Platform',
                trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                onTap: () => _showInfoDialog(
                  'About Yukti-AI',
                  'Yukti-AI Business Automation is a business automation and CRM integration platform with mobile monitoring, reporting and automation capabilities.',
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // SECURITY NOTE
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(
                color: Colors.grey.shade200,
              ),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.shield_outlined,
                  color: Colors.green.shade700,
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'API keys, CRM passwords, authentication secrets and other sensitive credentials must never be displayed or stored directly in the application.',
                    style: TextStyle(
                      fontSize: 12.5,
                      height: 1.5,
                      color: Colors.black54,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}


// ============================================================
// SETTINGS SECTION
// ============================================================

Widget _settingsSection({
  required String title,
  required String subtitle,
  required IconData icon,
  required List<Widget> children,
}) {
  return Container(
    width: double.infinity,
    padding: const EdgeInsets.fromLTRB(16, 16, 16, 14),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      border: Border.all(
        color: Colors.grey.shade200,
      ),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: const Color(0xFFEFF2FF),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                color: const Color(0xFF3157D5),
                size: 21,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 11.5,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        ...children,
      ],
    ),
  );
}


// ============================================================
// SETTINGS ROW
// ============================================================

Widget _settingsRow({
  required IconData icon,
  required String title,
  required String value,
  Color? valueColor,
  Widget? trailing,
  VoidCallback? onTap,
}) {
  return InkWell(
    onTap: onTap,
    borderRadius: BorderRadius.circular(13),
    child: Padding(
      padding: const EdgeInsets.symmetric(
        vertical: 10,
        horizontal: 4,
      ),
      child: Row(
        children: [
          Icon(
            icon,
            size: 21,
            color: Colors.grey.shade700,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 13.5,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  value,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontSize: 11.5,
                    color: valueColor ?? Colors.grey.shade600,
                    fontWeight: valueColor != null
                        ? FontWeight.w700
                        : FontWeight.w400,
                  ),
                ),
              ],
            ),
          ),
          if (trailing != null) trailing,
        ],
      ),
    ),
  );
}


// ============================================================
// API URL
// ============================================================

void _showApiUrlDialog() {
  final controller = TextEditingController(
    text: apiBaseUrl,
  );

  showDialog(
    context: context,
    builder: (dialogContext) {
      return AlertDialog(
        title: const Text('Yukti-AI API URL'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Current API endpoint used by the mobile application.',
              style: TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 15),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: 'API URL',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Production deployment will use HTTPS. API keys and secrets must not be entered here.',
              style: TextStyle(
                fontSize: 11.5,
                color: Colors.grey,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('CANCEL'),
          ),
          FilledButton(
            onPressed: () {
              final value = controller.text.trim();
              final uri = Uri.tryParse(value);
              if (uri == null || uri.host.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Please enter a valid API URL.')),
                );
                return;
              }

              setState(() {
                apiBaseUrl = value.endsWith('/')
                    ? value.substring(0, value.length - 1)
                    : value;
              });

              Navigator.pop(dialogContext);
              fetchData();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('API URL updated for this session.')),
              );
            },
            child: const Text('SAVE'),
          ),
        ],
      );
    },
  );
}


// ============================================================
// INFORMATION DIALOG
// ============================================================

void _showInfoDialog(
  String title,
  String message,
) {
  showDialog(
    context: context,
    builder: (dialogContext) {
      return AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('OK'),
          ),
        ],
      );
    },
  );
}


// ============================================================
// TWO FACTOR AUTHENTICATION
// ============================================================

void _showTwoFactorDialog() {
  showDialog(
    context: context,
    builder: (dialogContext) {
      return AlertDialog(
        title: const Row(
          children: [
            Icon(
              Icons.security_rounded,
              color: Color(0xFF3157D5),
            ),
            SizedBox(width: 10),
            Expanded(
              child: Text('Two-Factor Authentication'),
            ),
          ],
        ),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Protect your Yukti-AI account with an additional verification step.',
            ),
            SizedBox(height: 16),
            Text(
              'Available methods:',
              style: TextStyle(
                fontWeight: FontWeight.w800,
              ),
            ),
            SizedBox(height: 8),
            Text('• Google Authenticator'),
            Text('• Microsoft Authenticator'),
            Text('• QR-code registration'),
            Text('• Manual setup key'),
            Text('• Six-digit authenticator OTP'),
            Text('• Recovery OTP / recovery codes'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('CLOSE'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.pop(dialogContext);
              _showAuthenticatorDialog();
            },
            child: const Text('SET UP 2FA'),
          ),
        ],
      );
    },
  );
}


// ============================================================
// AUTHENTICATOR
// ============================================================

void _showAuthenticatorDialog() {
  final otpController = TextEditingController();

  bool loading = true;
  bool setupRequested = false;
  bool verifying = false;
  String? qrUri;
  String? manualKey;
  String? errorMessage;

  Future<void> loadAuthenticator(StateSetter setDialogState) async {
    setDialogState(() {
      loading = true;
      errorMessage = null;
    });

    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/api/mobile/auth/totp/setup'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'account_id': 'yuktiai-mobile',
          'issuer': 'Yukti-AI Business Automation',
          'account_name': 'Yukti-AI Mobile',
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      if (response.statusCode != 200 || data['success'] != true) {
        throw Exception(data['message'] ?? 'Unable to create authenticator setup.');
      }

      setDialogState(() {
        qrUri = data['otpauth_uri']?.toString();
        manualKey = data['secret']?.toString();
        loading = false;
      });
    } catch (e) {
      setDialogState(() {
        loading = false;
        errorMessage = e.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  Future<void> verifyAuthenticator(
    StateSetter setDialogState,
    BuildContext dialogContext,
  ) async {
    final code = otpController.text.trim();

    if (!RegExp(r'^\d{6}$').hasMatch(code)) {
      setDialogState(() => errorMessage = 'Enter the 6-digit authenticator code.');
      return;
    }

    setDialogState(() {
      verifying = true;
      errorMessage = null;
    });

    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/api/mobile/auth/totp/verify'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'account_id': 'yuktiai-mobile',
          'code': code,
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      if (response.statusCode != 200 || data['success'] != true) {
        throw Exception(data['message'] ?? 'Authenticator verification failed.');
      }

      if (!mounted) return;

      await fetchTwoFactorStatus();
      Navigator.pop(dialogContext);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Authenticator verified and enabled.')),
      );
    } catch (e) {
      setDialogState(() {
        verifying = false;
        errorMessage = e.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  showDialog(
    context: context,
    builder: (dialogContext) {
      return StatefulBuilder(
        builder: (context, setDialogState) {
          if (loading && !setupRequested && qrUri == null && errorMessage == null) {
            setupRequested = true;
            loadAuthenticator(setDialogState);
          }

          return AlertDialog(
            title: const Row(
              children: [
                Icon(Icons.qr_code_2_rounded, color: Color(0xFF3157D5)),
                SizedBox(width: 10),
                Expanded(child: Text('Authenticator Setup')),
              ],
            ),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (loading)
                    const SizedBox(
                      width: 190,
                      height: 190,
                      child: Center(child: CircularProgressIndicator()),
                    )
                  else if (qrUri != null)
                    Container(
                      width: 220,
                      height: 220,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: QrImageView(
                        data: qrUri!,
                        version: QrVersions.auto,
                        size: 196,
                        backgroundColor: Colors.white,
                      ),
                    ),
                  const SizedBox(height: 16),
                  const Text(
                    'Scan this QR code with Google Authenticator or Microsoft Authenticator.',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 13),
                  ),
                  if (manualKey != null) ...[
                    const SizedBox(height: 12),
                    ExpansionTile(
                      tilePadding: EdgeInsets.zero,
                      title: const Text('Manual setup key'),
                      children: [
                        SelectableText(
                          manualKey!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontWeight: FontWeight.w700,
                            letterSpacing: 1.2,
                          ),
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'Keep this key private. It can generate your authenticator codes.',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 11, color: Colors.grey),
                        ),
                      ],
                    ),
                  ],
                  const SizedBox(height: 12),
                  TextField(
                    controller: otpController,
                    keyboardType: TextInputType.number,
                    maxLength: 6,
                    textAlign: TextAlign.center,
                    decoration: const InputDecoration(
                      labelText: '6-digit authenticator code',
                      hintText: '000000',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  if (errorMessage != null) ...[
                    const SizedBox(height: 10),
                    Text(
                      errorMessage!,
                      style: TextStyle(color: Colors.red.shade700, fontSize: 12.5),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext),
                child: const Text('CANCEL'),
              ),
              FilledButton(
                onPressed: loading || verifying || qrUri == null
                    ? null
                    : () => verifyAuthenticator(setDialogState, dialogContext),
                child: verifying
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Text('VERIFY & ENABLE'),
              ),
            ],
          );
        },
      );
    },
  );
}


// ============================================================
// OTP FALLBACK
// ============================================================

void _showOtpDialog() {
  final destinationController = TextEditingController();
  final otpController = TextEditingController();

  bool otpSent = false;
  bool sending = false;
  bool verifying = false;
  String? requestId;
  String? errorMessage;

  Future<void> sendOtp(StateSetter setDialogState) async {
    final destination = destinationController.text.trim();

    if (destination.isEmpty) {
      setDialogState(() => errorMessage = 'Enter a mobile number or email address.');
      return;
    }

    setDialogState(() {
      sending = true;
      errorMessage = null;
    });

    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/api/mobile/auth/otp/request'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'destination': destination,
          'purpose': 'settings_2fa',
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);

      if (response.statusCode != 200 || data['success'] != true) {
        throw Exception(data['message'] ?? 'Unable to send OTP.');
      }

      setDialogState(() {
        otpSent = true;
        requestId = data['request_id']?.toString();
        sending = false;
        errorMessage = null;
      });
    } catch (e) {
      setDialogState(() {
        sending = false;
        errorMessage = e.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  Future<void> verifyOtp(
    StateSetter setDialogState,
    BuildContext dialogContext,
  ) async {
    final destination = destinationController.text.trim();
    final otp = otpController.text.trim();

    if (otp.length != 6 || !RegExp(r'^\d{6}$').hasMatch(otp)) {
      setDialogState(() => errorMessage = 'Enter the 6-digit OTP.');
      return;
    }

    setDialogState(() {
      verifying = true;
      errorMessage = null;
    });

    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/api/mobile/auth/otp/verify'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'destination': destination,
          'otp': otp,
          'request_id': requestId,
          'purpose': 'settings_2fa',
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);

      if (response.statusCode != 200 || data['success'] != true) {
        throw Exception(data['message'] ?? 'OTP verification failed.');
      }

      if (!mounted) return;

      Navigator.pop(dialogContext);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('OTP verified successfully.')),
      );
    } catch (e) {
      setDialogState(() {
        verifying = false;
        errorMessage = e.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  showDialog(
    context: context,
    builder: (dialogContext) {
      return StatefulBuilder(
        builder: (context, setDialogState) {
          return AlertDialog(
            title: const Row(
              children: [
                Icon(Icons.sms_outlined, color: Color(0xFF3157D5)),
                SizedBox(width: 10),
                Expanded(child: Text('OTP Verification')),
              ],
            ),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'Enter your registered mobile number or email address. '
                    'A 6-digit OTP will be sent for verification.',
                  ),
                  const SizedBox(height: 18),
                  TextField(
                    controller: destinationController,
                    keyboardType: TextInputType.emailAddress,
                    enabled: !sending && !verifying,
                    decoration: const InputDecoration(
                      labelText: 'Mobile Number or Email ID',
                      hintText: 'example@company.com / +91XXXXXXXXXX',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.alternate_email_rounded),
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      onPressed: sending ? null : () => sendOtp(setDialogState),
                      icon: sending
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.send_rounded),
                      label: Text(sending ? 'SENDING...' : 'SEND OTP'),
                    ),
                  ),
                  if (otpSent) ...[
                    const SizedBox(height: 18),
                    TextField(
                      controller: otpController,
                      keyboardType: TextInputType.number,
                      maxLength: 6,
                      textAlign: TextAlign.center,
                      decoration: const InputDecoration(
                        labelText: '6-digit OTP',
                        hintText: '000000',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton(
                            onPressed: sending ? null : () => sendOtp(setDialogState),
                            child: const Text('RESEND OTP'),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: FilledButton(
                            onPressed: verifying
                                ? null
                                : () => verifyOtp(setDialogState, dialogContext),
                            child: verifying
                                ? const SizedBox(
                                    width: 18,
                                    height: 18,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: Colors.white,
                                    ),
                                  )
                                : const Text('VERIFY OTP'),
                          ),
                        ),
                      ],
                    ),
                  ],
                  if (errorMessage != null) ...[
                    const SizedBox(height: 12),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.red.shade50,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        errorMessage!,
                        style: TextStyle(color: Colors.red.shade700, fontSize: 12.5),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext),
                child: const Text('CANCEL'),
              ),
            ],
          );
        },
      );
    },
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
              'Live leads by project',
              Icons.business_outlined,
              Column(
                children: projects
                    .where((p) => p != 'All')
                    .map((p) => _project(
                          p,
                          totalLeads == 0
                              ? 0
                              : (projectCounts[p] ?? 0) / totalLeads,
                          projectCounts[p] ?? 0,
                        ))
                    .toList(),
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
                  _status('In4 CRM Report', 'Connected'),
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

  void _showNotificationsDialog() {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.notifications_none_rounded, color: Color(0xFF3157D5)),
            SizedBox(width: 10),
            Text('Notifications'),
          ],
        ),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: Icon(Icons.smart_toy_outlined),
              title: Text('Automation Alerts'),
              subtitle: Text('Enabled'),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: Icon(Icons.cloud_upload_outlined),
              title: Text('CRM Upload Alerts'),
              subtitle: Text('Enabled'),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: Icon(Icons.sync_problem_outlined),
              title: Text('Sync Alerts'),
              subtitle: Text('Enabled'),
            ),
          ],
        ),
        actions: [
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('CLOSE'),
          ),
        ],
      ),
    );
  }

  Widget _header() => Row(
        children: [
          // Full Yukti-AI Business Automation branding on the Dashboard.
          // The separate icon-only asset is still used where a compact logo
          // is required elsewhere in the app.
          SizedBox(
            width: 190,
            height: 62,
            child: Image.asset(
              'assets/images/yukti_ai_business_automation_logo.png',
              fit: BoxFit.contain,
              alignment: Alignment.centerLeft,
            ),
          ),
          const Spacer(),
          IconButton(
            tooltip: 'Notifications',
            onPressed: _showNotificationsDialog,
            icon: const Icon(Icons.notifications_none_rounded),
          ),
          IconButton(
            tooltip: 'Log Off',
            onPressed: _logOff,
            icon: const Icon(Icons.logout_rounded),
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
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isConnected
                        ? 'In4 CRM Connected'
                        : 'In4 CRM Connection Unavailable',
                    style: TextStyle(
                      fontWeight: FontWeight.w700,
                      color: isConnected
                          ? const Color(0xFF187847)
                          : const Color(0xFF9A641C),
                    ),
                  ),
                  if (isConnected && lastSync != null)
                    Text(
                      'Last sync: $lastSync',
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.grey.shade600,
                      ),
                    ),
                ],
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


// ============================================================
// LEADS SCREEN - LIVE IN4 LEAD MANAGEMENT
// ============================================================

class LeadsScreen extends StatefulWidget {
  final String apiBaseUrl;
  final String initialPeriod;

  const LeadsScreen({
    super.key,
    required this.apiBaseUrl,
    required this.initialPeriod,
  });

  @override
  State<LeadsScreen> createState() => _LeadsScreenState();
}

class _LeadsScreenState extends State<LeadsScreen> {
  late String selectedPeriod;
  String selectedProject = 'All';
  String selectedSource = 'All';
  String selectedUser = 'All';

  final searchController = TextEditingController();

  bool loading = true;
  String? error;

  int totalLeads = 0;
  int todayLeads = 0;

  List<String> projects = ['All'];
  List<String> sources = ['All'];
  List<String> users = ['All'];

  List<Map<String, dynamic>> leads = [];

  final periods = const [
    'Today',
    'Yesterday',
    'This Week',
    'This Month',
    'Last Month',
  ];

  @override
  void initState() {
    super.initState();
    selectedPeriod = periods.contains(widget.initialPeriod)
        ? widget.initialPeriod
        : 'This Month';
    fetchLeads();
  }

  @override
  void dispose() {
    searchController.dispose();
    super.dispose();
  }

  String _periodValue(String value) {
    switch (value) {
      case 'Today':
        return 'today';
      case 'Yesterday':
        return 'yesterday';
      case 'This Week':
        return 'this_week';
      case 'Last Month':
        return 'last_month';
      default:
        return 'this_month';
    }
  }

  Future<void> fetchLeads() async {
    if (!mounted) return;

    setState(() {
      loading = true;
      error = null;
    });

    try {
      final query = <String, String>{
        'period': _periodValue(selectedPeriod),
        'project': selectedProject,
        'source': selectedSource,
        'user': selectedUser,
        'search': searchController.text.trim(),
      };

      final uri = Uri.parse(
        '${widget.apiBaseUrl}/api/mobile/leads',
      ).replace(queryParameters: query);

      final response =
          await http.get(uri).timeout(const Duration(seconds: 10));

      if (response.statusCode != 200) {
        throw Exception('Server returned ${response.statusCode}');
      }

      final data = json.decode(response.body);

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'Unable to load leads.');
      }

      final nextProjects = <String>['All'];
      final nextSources = <String>['All'];
      final nextUsers = <String>['All'];

      if (data['available_projects'] is List) {
        for (final item in data['available_projects']) {
          final value = '$item'.trim();
          if (value.isNotEmpty && !nextProjects.contains(value)) {
            nextProjects.add(value);
          }
        }
      }

      if (data['available_sources'] is List) {
        for (final item in data['available_sources']) {
          final value = '$item'.trim();
          if (value.isNotEmpty && !nextSources.contains(value)) {
            nextSources.add(value);
          }
        }
      }

      if (data['available_users'] is List) {
        for (final item in data['available_users']) {
          final value = '$item'.trim();
          if (value.isNotEmpty && !nextUsers.contains(value)) {
            nextUsers.add(value);
          }
        }
      }

      final nextLeads = <Map<String, dynamic>>[];
      if (data['leads'] is List) {
        for (final item in data['leads']) {
          if (item is Map) {
            nextLeads.add(Map<String, dynamic>.from(item));
          }
        }
      }

      if (!mounted) return;

      setState(() {
        totalLeads = _intValue(data['total_leads']);
        todayLeads = _intValue(data['today_leads']);

        projects = nextProjects;
        sources = nextSources;
        users = nextUsers;

        if (!projects.contains(selectedProject)) selectedProject = 'All';
        if (!sources.contains(selectedSource)) selectedSource = 'All';
        if (!users.contains(selectedUser)) selectedUser = 'All';

        leads = nextLeads;
        loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        loading = false;
        leads = [];
        error = e.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  int _intValue(dynamic value) =>
      value is int ? value : int.tryParse('$value') ?? 0;

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: fetchLeads,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(20, 18, 20, 30),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Leads',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      SizedBox(height: 5),
                      Text(
                        'Live CRM lead management',
                        style: TextStyle(
                          fontSize: 13,
                          color: Color(0xFF777B87),
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  onPressed: loading ? null : fetchLeads,
                  icon: const Icon(Icons.refresh_rounded),
                ),
              ],
            ),
            const SizedBox(height: 18),

            _leadFilter(
              'PERIOD',
              selectedPeriod,
              periods,
              Icons.calendar_today_outlined,
              (value) {
                if (value == null) return;
                setState(() => selectedPeriod = value);
                fetchLeads();
              },
            ),
            const SizedBox(height: 10),

            Row(
              children: [
                Expanded(
                  child: _leadFilter(
                    'PROJECT',
                    selectedProject,
                    projects,
                    Icons.business_outlined,
                    (value) {
                      if (value == null) return;
                      setState(() => selectedProject = value);
                      fetchLeads();
                    },
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _leadFilter(
                    'SOURCE',
                    selectedSource,
                    sources,
                    Icons.campaign_outlined,
                    (value) {
                      if (value == null) return;
                      setState(() => selectedSource = value);
                      fetchLeads();
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),

            _leadFilter(
              'ASSIGNED USER',
              selectedUser,
              users,
              Icons.person_outline_rounded,
              (value) {
                if (value == null) return;
                setState(() => selectedUser = value);
                fetchLeads();
              },
            ),
            const SizedBox(height: 12),

            TextField(
              controller: searchController,
              textInputAction: TextInputAction.search,
              onSubmitted: (_) => fetchLeads(),
              decoration: InputDecoration(
                hintText:
                    'Search customer, opportunity, mobile, project or source',
                prefixIcon: const Icon(Icons.search_rounded),
                suffixIcon: IconButton(
                  onPressed: () {
                    searchController.clear();
                    fetchLeads();
                  },
                  icon: const Icon(Icons.clear_rounded),
                ),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 18),

            Row(
              children: [
                Expanded(
                  child: _leadKpi(
                    'TOTAL LEADS',
                    '$totalLeads',
                    Icons.groups_rounded,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _leadKpi(
                    "TODAY'S LEADS",
                    '$todayLeads',
                    Icons.today_rounded,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            if (loading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(45),
                  child: CircularProgressIndicator(),
                ),
              )
            else if (error != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(22),
                  child: Column(
                    children: [
                      const Icon(
                        Icons.cloud_off_rounded,
                        size: 42,
                        color: Color(0xFFE99A2E),
                      ),
                      const SizedBox(height: 10),
                      const Text(
                        'Lead data unavailable',
                        style: TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        error!,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontSize: 12,
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 14),
                      FilledButton.icon(
                        onPressed: fetchLeads,
                        icon: const Icon(Icons.refresh_rounded),
                        label: const Text('RETRY'),
                      ),
                    ],
                  ),
                ),
              )
            else if (leads.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(28),
                  child: Center(
                    child: Text(
                      'No leads found for the selected filters.',
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              )
            else
              ...leads.map(_leadCard),
          ],
        ),
      ),
    );
  }

  Widget _leadKpi(String title, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(17),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            blurRadius: 24,
            offset: const Offset(0, 7),
            color: Colors.black.withValues(alpha: .04),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: const Color(0xFF3157D5), size: 24),
          const SizedBox(height: 13),
          Text(
            title,
            style: const TextStyle(
              fontSize: 10,
              letterSpacing: .7,
              fontWeight: FontWeight.w800,
              color: Color(0xFF888C97),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              fontSize: 27,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }

  Widget _leadFilter(
    String label,
    String value,
    List<String> items,
    IconData icon,
    ValueChanged<String?> onChanged,
  ) {
    final safeValue = items.contains(value) ? value : items.first;

    return Container(
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
              Text(
                label,
                style: const TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.w800,
                  letterSpacing: .7,
                  color: Color(0xFF898D98),
                ),
              ),
            ],
          ),
          DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: safeValue,
              isExpanded: true,
              icon: const Icon(Icons.keyboard_arrow_down_rounded),
              items: items
                  .map(
                    (item) => DropdownMenuItem(
                      value: item,
                      child: Text(
                        item,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  )
                  .toList(),
              onChanged: onChanged,
            ),
          ),
        ],
      ),
    );
  }

  Widget _leadCard(Map<String, dynamic> lead) {
    String value(String key) => '${lead[key] ?? ''}'.trim();

    final customer = value('Customer Name').isEmpty
        ? 'Unnamed Lead'
        : value('Customer Name');

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            blurRadius: 18,
            offset: const Offset(0, 6),
            color: Colors.black.withValues(alpha: .035),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const CircleAvatar(
                radius: 20,
                backgroundColor: Color(0xFFEFF2FF),
                child: Icon(
                  Icons.person_rounded,
                  color: Color(0xFF3157D5),
                ),
              ),
              const SizedBox(width: 11),
              Expanded(
                child: Text(
                  customer,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _leadDetail('Opportunity ID', value('Opportunity ID')),
          _leadDetail('Contact Number', value('Contact Number')),
          _leadDetail('Project', value('Project Name')),
          _leadDetail('Source', value('Enquiry Source')),
          _leadDetail('Assigned To', value('Assinged To')),
          _leadDetail('Assigned Date', value('Assinged Date')),
        ],
      ),
    );
  }

  Widget _leadDetail(String label, String value) {
    if (value.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(top: 7),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 112,
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 11,
                color: Color(0xFF8A8E99),
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}


// ============================================================
// AUTOMATION SCREEN - READ-ONLY MONITORING
// ============================================================

class AutomationScreen extends StatefulWidget {
  final String apiBaseUrl;

  const AutomationScreen({
    super.key,
    required this.apiBaseUrl,
  });

  @override
  State<AutomationScreen> createState() => _AutomationScreenState();
}

class _AutomationScreenState extends State<AutomationScreen> {
  bool loading = true;
  String? error;
  DateTime? lastRefresh;

  List<Map<String, dynamic>> automations = [];

  final fallbackNames = const [
    'Outlook Lead Reader',
    'Excel / Master File',
    'In4 CRM Report',
    'Google Sheet → CRM',
    'CRM Lead Upload',
    'Dashboard Sync',
  ];

  @override
  void initState() {
    super.initState();
    fetchAutomationStatus();
  }

  Future<void> fetchAutomationStatus() async {
    if (!mounted) return;

    setState(() {
      loading = true;
      error = null;
    });

    try {
      final uri = Uri.parse(
        '${widget.apiBaseUrl}/api/mobile/automation-status',
      );

      final response =
          await http.get(uri).timeout(const Duration(seconds: 10));

      if (response.statusCode != 200) {
        throw Exception('Server returned ${response.statusCode}');
      }

      final data = json.decode(response.body);

      if (data['success'] != true) {
        throw Exception(
          data['message'] ?? 'Automation status unavailable.',
        );
      }

      final rows = <Map<String, dynamic>>[];

      if (data['automations'] is List) {
        for (final item in data['automations']) {
          if (item is Map) {
            rows.add(Map<String, dynamic>.from(item));
          }
        }
      }

      if (!mounted) return;

      setState(() {
        automations = rows;
        loading = false;
        lastRefresh = DateTime.now();
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        loading = false;
        error = e.toString().replaceFirst('Exception: ', '');
        lastRefresh = DateTime.now();
      });
    }
  }

  Map<String, dynamic>? _find(String name) {
    for (final item in automations) {
      final current = '${item['automation_name'] ?? ''}'.trim();
      if (current.toLowerCase() == name.toLowerCase()) {
        return item;
      }
    }
    return null;
  }

  String _status(Map<String, dynamic>? item) {
    if (item == null) return 'Not reported';

    final value = '${item['status'] ?? ''}'.trim();
    return value.isEmpty ? 'Idle' : value;
  }

  Color _statusColor(String status) {
    final value = status.toLowerCase();

    if (value.contains('fail') || value.contains('error')) {
      return Colors.red;
    }

    if (value.contains('run') || value.contains('process')) {
      return const Color(0xFFE99A2E);
    }

    if (value.contains('success') ||
        value.contains('healthy') ||
        value.contains('complete') ||
        value.contains('connected')) {
      return Colors.green;
    }

    return Colors.grey.shade700;
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: fetchAutomationStatus,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(20, 18, 20, 30),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Automation',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      SizedBox(height: 5),
                      Text(
                        'Monitor your automation environment',
                        style: TextStyle(
                          fontSize: 13,
                          color: Color(0xFF777B87),
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  onPressed: loading ? null : fetchAutomationStatus,
                  icon: const Icon(Icons.refresh_rounded),
                ),
              ],
            ),
            const SizedBox(height: 18),

            _automationSummary(),
            const SizedBox(height: 18),

            if (loading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(45),
                  child: CircularProgressIndicator(),
                ),
              )
            else if (error != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(22),
                  child: Column(
                    children: [
                      const Icon(
                        Icons.cloud_off_rounded,
                        size: 42,
                        color: Color(0xFFE99A2E),
                      ),
                      const SizedBox(height: 10),
                      const Text(
                        'Automation status unavailable',
                        style: TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 7),
                      Text(
                        error!,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontSize: 12,
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 14),
                      FilledButton.icon(
                        onPressed: fetchAutomationStatus,
                        icon: const Icon(Icons.refresh_rounded),
                        label: const Text('RETRY'),
                      ),
                    ],
                  ),
                ),
              )
            else
              ...fallbackNames.map(_automationCard),

            if (lastRefresh != null) ...[
              const SizedBox(height: 12),
              Center(
                child: Text(
                  'Last checked: ${lastRefresh!.toLocal()}',
                  style: const TextStyle(
                    fontSize: 10,
                    color: Color(0xFF9295A0),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _automationSummary() {
    var running = 0;
    var failed = 0;
    var healthy = 0;

    for (final item in automations) {
      final status = _status(item).toLowerCase();
      if (status.contains('fail') || status.contains('error')) {
        failed++;
      } else if (status.contains('run') || status.contains('process')) {
        running++;
      } else if (status != 'not reported') {
        healthy++;
      }
    }

    return Row(
      children: [
        Expanded(
          child: _automationKpi(
            'HEALTHY',
            '$healthy',
            Icons.check_circle_outline_rounded,
            Colors.green,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _automationKpi(
            'RUNNING',
            '$running',
            Icons.sync_rounded,
            const Color(0xFFE99A2E),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _automationKpi(
            'FAILED',
            '$failed',
            Icons.error_outline_rounded,
            Colors.red,
          ),
        ),
      ],
    );
  }

  Widget _automationKpi(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(13),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 21),
          const SizedBox(height: 9),
          Text(
            title,
            style: const TextStyle(
              fontSize: 9,
              fontWeight: FontWeight.w800,
              color: Color(0xFF888C97),
            ),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: const TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }

  Widget _automationCard(String name) {
    final item = _find(name);
    final status = _status(item);
    final color = _statusColor(status);

    final lastRun =
        '${item?['last_run'] ?? 'Not available'}'.trim();
    final records =
        '${item?['records'] ?? 0}'.trim();
    final errorText =
        '${item?['error'] ?? ''}'.trim();

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 43,
                height: 43,
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF2FF),
                  borderRadius: BorderRadius.circular(13),
                ),
                child: const Icon(
                  Icons.smart_toy_outlined,
                  color: Color(0xFF3157D5),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  name,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 9,
                  vertical: 5,
                ),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: .10),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  status,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                    color: color,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _automationDetail('Last Run', lastRun),
          _automationDetail('Records', records),
          if (errorText.isNotEmpty)
            _automationDetail('Error', errorText),
        ],
      ),
    );
  }

  Widget _automationDetail(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(top: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 75,
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 11,
                color: Color(0xFF8A8E99),
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}


class ReportsScreen extends StatefulWidget {
  final String apiBaseUrl;
  final String initialPeriod;

  const ReportsScreen({
    super.key,
    required this.apiBaseUrl,
    required this.initialPeriod,
  });

  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  late String selectedPeriod;
  bool loading = true;
  String? error;
  int totalLeads = 0;
  Map<String, dynamic> users = {};

  final periods = const ['Today', 'Yesterday', 'This Week', 'This Month', 'Last Month'];

  @override
  void initState() {
    super.initState();
    selectedPeriod = periods.contains(widget.initialPeriod) ? widget.initialPeriod : 'This Month';
    fetchReport();
  }

  String _apiPeriod(String p) {
    switch (p) {
      case 'Today': return 'today';
      case 'Yesterday': return 'yesterday';
      case 'This Week': return 'this_week';
      case 'Last Month': return 'last_month';
      default: return 'this_month';
    }
  }

  int _int(dynamic v) => v is int ? v : int.tryParse('$v') ?? 0;

  int _total(dynamic map) {
    if (map is! Map) return 0;
    var n = 0;
    map.forEach((_, v) => n += _int(v));
    return n;
  }

  Future<void> fetchReport() async {
    setState(() { loading = true; error = null; });
    try {
      final uri = Uri.parse('${widget.apiBaseUrl}/api/mobile/in4-data?period=${Uri.encodeComponent(_apiPeriod(selectedPeriod))}');
      final response = await http.get(uri).timeout(const Duration(seconds: 10));
      if (response.statusCode != 200) throw Exception('Server returned ${response.statusCode}');
      final data = json.decode(response.body);
      if (data['success'] != true) throw Exception(data['message'] ?? 'Report error');
      final raw = data['user_project_source_counts'];
      final parsed = <String, dynamic>{};
      if (raw is Map) raw.forEach((k, v) => parsed['$k'] = v);
      if (!mounted) return;
      setState(() {
        totalLeads = _int(data['total_leads']);
        users = parsed;
        loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() { loading = false; error = 'Unable to load report data.'; });
    }
  }

  Future<List<List<String>>> _reportRows() async {
    final rows = <List<String>>[
      ['User Name', 'Project', 'Source', 'Lead Count'],
    ];

    users.forEach((user, projectData) {
      if (projectData is! Map) return;
      projectData.forEach((project, sourceData) {
        if (sourceData is! Map) return;
        sourceData.forEach((source, count) {
          rows.add([
            '$user',
            '$project',
            '$source',
            '${_int(count)}',
          ]);
        });
      });
    });

    return rows;
  }

  Future<void> _exportExcel() async {
    if (loading || error != null || users.isEmpty) return;

    try {
      final rows = await _reportRows();
      final excelFile = excel.Excel.createExcel();

// First create the Report sheet.
// This gives the workbook 2 sheets: Sheet1 + Report.
      final sheet = excelFile['Report'];

// Now Sheet1 can be safely deleted.
      if (excelFile.sheets.containsKey('Sheet1')) {
      excelFile.delete('Sheet1');
}   
      
      
      sheet.appendRow([
  excel.TextCellValue('Yukti-AI Business Automation'),
]);

sheet.appendRow([
  excel.TextCellValue('Lead Report - $selectedPeriod'),
]);

sheet.appendRow([
  excel.TextCellValue('Total Leads'),
  excel.IntCellValue(totalLeads),
]);
      sheet.appendRow([]);

      for (final row in rows) {
        sheet.appendRow([
          excel.TextCellValue(row[0]),
          excel.TextCellValue(row[1]),
          excel.TextCellValue(row[2]),
          excel.IntCellValue(_int(row[3])),
        ]);
      }

      final bytes = excelFile.encode();
      if (bytes == null) throw Exception('Unable to create Excel file.');

      final dir = await getApplicationDocumentsDirectory();
      final safePeriod = selectedPeriod.replaceAll(' ', '_');
      final file = File(
        '${dir.path}/YuktiAI_Lead_Report_$safePeriod.xlsx',
      );
      await file.writeAsBytes(bytes, flush: true);

      await SharePlus.instance.share(
        ShareParams(
          files: [XFile(file.path)],
          subject: 'Yukti-AI Lead Report - $selectedPeriod',
          text: 'Yukti-AI Business Automation Lead Report - $selectedPeriod',
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Excel export failed: $e')),
      );
    }
  }

  Future<void> _exportPdf() async {
    if (loading || error != null || users.isEmpty) return;

    try {
      final rows = await _reportRows();
      final pdf = pw.Document();

      pdf.addPage(
        pw.MultiPage(
          pageFormat: PdfPageFormat.a4,
          margin: const pw.EdgeInsets.all(28),
          build: (context) => [
            pw.Text(
              'Yukti-AI Business Automation',
              style: pw.TextStyle(
                fontSize: 20,
                fontWeight: pw.FontWeight.bold,
              ),
            ),
            pw.SizedBox(height: 6),
            pw.Text(
              'Lead Report - $selectedPeriod',
              style: const pw.TextStyle(fontSize: 13),
            ),
            pw.SizedBox(height: 4),
            pw.Text('Total Leads: $totalLeads'),
            pw.SizedBox(height: 18),
            pw.Table.fromTextArray(
              headers: rows.first,
              data: rows.skip(1).toList(),
              headerStyle: pw.TextStyle(
                fontWeight: pw.FontWeight.bold,
                fontSize: 9,
              ),
              cellStyle: const pw.TextStyle(fontSize: 8),
              cellPadding: const pw.EdgeInsets.all(5),
              border: pw.TableBorder.all(
                color: PdfColors.grey400,
                width: .5,
              ),
            ),
          ],
        ),
      );

      final dir = await getApplicationDocumentsDirectory();
      final safePeriod = selectedPeriod.replaceAll(' ', '_');
      final file = File(
        '${dir.path}/YuktiAI_Lead_Report_$safePeriod.pdf',
      );
      await file.writeAsBytes(await pdf.save(), flush: true);

      await SharePlus.instance.share(
        ShareParams(
          files: [XFile(file.path)],
          subject: 'Yukti-AI Lead Report - $selectedPeriod',
          text: 'Yukti-AI Business Automation Lead Report - $selectedPeriod',
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('PDF export failed: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: fetchReport,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(20, 18, 20, 30),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Reports', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800)),
              SizedBox(height: 5),
              Text('Lead performance by user, project and source.', style: TextStyle(fontSize: 13, color: Color(0xFF777B87))),
            ])),
            IconButton(onPressed: loading ? null : fetchReport, icon: const Icon(Icons.refresh_rounded)),
          ]),
          const SizedBox(height: 18),
          _periodFilter(),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: (loading || error != null || users.isEmpty) ? null : _exportPdf,
                  icon: const Icon(Icons.picture_as_pdf_outlined),
                  label: const Text('Export PDF'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: (loading || error != null || users.isEmpty) ? null : _exportExcel,
                  icon: const Icon(Icons.table_view_outlined),
                  label: const Text('Export Excel'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          _summary(),
          const SizedBox(height: 22),
          if (loading) const Center(child: Padding(padding: EdgeInsets.all(40), child: CircularProgressIndicator()))
          else if (error != null) _error()
          else if (users.isEmpty) _empty()
          else ..._userCards(),
        ]),
      ),
    );
  }

  Widget _periodFilter() => Container(
    width: double.infinity,
    padding: const EdgeInsets.fromLTRB(14, 8, 10, 4),
    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('REPORT PERIOD', style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, letterSpacing: .7, color: Color(0xFF898D98))),
      DropdownButtonHideUnderline(child: DropdownButton<String>(
        value: selectedPeriod,
        isExpanded: true,
        items: periods.map((p) => DropdownMenuItem(value: p, child: Text(p))).toList(),
        onChanged: (v) { if (v == null) return; setState(() => selectedPeriod = v); fetchReport(); },
      )),
    ]),
  );

  Widget _summary() => Container(
    width: double.infinity,
    padding: const EdgeInsets.all(18),
    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20), boxShadow: [BoxShadow(blurRadius: 24, offset: const Offset(0, 7), color: Colors.black.withValues(alpha: .04))]),
    child: Row(children: [
      Container(width: 48, height: 48, decoration: BoxDecoration(color: const Color(0xFFEFF2FF), borderRadius: BorderRadius.circular(14)), child: const Icon(Icons.bar_chart_rounded, color: Color(0xFF3157D5))),
      const SizedBox(width: 14),
      Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('TOTAL LEADS', style: TextStyle(fontSize: 10, letterSpacing: .7, fontWeight: FontWeight.w800, color: Color(0xFF888C97))),
        Text('$totalLeads', style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800)),
        Text(selectedPeriod, style: const TextStyle(fontSize: 11, color: Color(0xFF9295A0))),
      ]),
    ]),
  );

  List<Widget> _userCards() {
    final out = <Widget>[];
    users.forEach((user, projectData) {
      if (projectData is! Map) return;
      var userTotal = 0;
      projectData.forEach((_, sources) => userTotal += _total(sources));
      out.add(Container(
        width: double.infinity,
        margin: const EdgeInsets.only(bottom: 18),
        padding: const EdgeInsets.fromLTRB(17, 17, 17, 18),
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20), boxShadow: [BoxShadow(blurRadius: 25, offset: const Offset(0, 7), color: Colors.black.withValues(alpha: .04))]),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            const Icon(Icons.person_outline_rounded, color: Color(0xFF3157D5)),
            const SizedBox(width: 10),
            Expanded(child: Text('$user', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800))),
            Text('$userTotal', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF3157D5))),
          ]),
          const SizedBox(height: 10),
          ..._projects(projectData),
        ]),
      ));
    });
    return out;
  }

  List<Widget> _projects(Map data) {
    final out = <Widget>[];
    data.forEach((project, sourceData) {
      if (sourceData is! Map) return;
      final total = _total(sourceData);
      out.add(Container(
        margin: const EdgeInsets.only(top: 8),
        padding: const EdgeInsets.fromLTRB(13, 12, 13, 12),
        decoration: BoxDecoration(color: const Color(0xFFF8F9FC), borderRadius: BorderRadius.circular(14)),
        child: Column(children: [
          Row(children: [
            const Icon(Icons.business_outlined, size: 17, color: Color(0xFF3157D5)),
            const SizedBox(width: 7),
            Expanded(child: Text('$project', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800))),
            Text('$total', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800)),
          ]),
          ..._sources(sourceData),
        ]),
      ));
    });
    return out;
  }

  List<Widget> _sources(Map data) => data.entries.map((e) => Padding(
    padding: const EdgeInsets.only(top: 7),
    child: Row(children: [
      const SizedBox(width: 24),
      const Icon(Icons.arrow_right_rounded, size: 17, color: Color(0xFF9295A0)),
      const SizedBox(width: 3),
      Expanded(child: Text('${e.key}', style: const TextStyle(fontSize: 12, color: Color(0xFF5E626E)))),
      Text('${_int(e.value)}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800)),
    ]),
  )).toList();

  Widget _empty() => const Card(child: Padding(padding: EdgeInsets.all(30), child: Center(child: Text('No lead assignments were found for this period.'))));

  Widget _error() => Card(child: Padding(padding: const EdgeInsets.all(22), child: Column(children: [
    const Icon(Icons.cloud_off_rounded, size: 40, color: Color(0xFFE99A2E)),
    const SizedBox(height: 10),
    const Text('Report unavailable', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
    const SizedBox(height: 12),
    FilledButton.icon(onPressed: fetchReport, icon: const Icon(Icons.refresh_rounded), label: const Text('Retry')),
  ])));
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
