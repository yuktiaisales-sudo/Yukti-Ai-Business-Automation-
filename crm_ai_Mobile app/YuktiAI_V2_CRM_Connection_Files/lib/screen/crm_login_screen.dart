import 'package:flutter/material.dart';
import 'dashboard.dart';

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

  Future<void> connect() async {
    if (username.text.trim().isEmpty || password.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter username and password.')),
      );
      return;
    }

    setState(() => connecting = true);

    // V2 UI flow. Real CRM authentication/API handshake comes next.
    await Future.delayed(const Duration(milliseconds: 900));

    if (!mounted) return;
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => DashboardScreen(crmUrl: widget.crmUrl)),
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
        title: const Text('CRM Login', style: TextStyle(fontWeight: FontWeight.w800)),
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
                const Icon(Icons.link_rounded, color: Color(0xFF3157D5)),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    widget.crmUrl,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w700),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 30),
          const Text(
            'Sign in to your CRM',
            style: TextStyle(fontSize: 29, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 9),
          Text(
            'Use the same CRM username and password you use on your computer.',
            style: TextStyle(color: Colors.grey.shade600, height: 1.5),
          ),
          const SizedBox(height: 28),
          const Text('Username', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
          const SizedBox(height: 8),
          TextField(
            controller: username,
            decoration: InputDecoration(
              hintText: 'Enter CRM username',
              prefixIcon: const Icon(Icons.person_outline_rounded),
              filled: true, fillColor: Colors.white,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(16),
                borderSide: BorderSide(color: Colors.grey.shade200),
              ),
            ),
          ),
          const SizedBox(height: 18),
          const Text('Password', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
          const SizedBox(height: 8),
          TextField(
            controller: password,
            obscureText: obscure,
            onSubmitted: (_) => connect(),
            decoration: InputDecoration(
              hintText: 'Enter CRM password',
              prefixIcon: const Icon(Icons.lock_outline_rounded),
              suffixIcon: IconButton(
                onPressed: () => setState(() => obscure = !obscure),
                icon: Icon(obscure ? Icons.visibility_outlined : Icons.visibility_off_outlined),
              ),
              filled: true, fillColor: Colors.white,
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
              onPressed: connecting ? null : connect,
              style: FilledButton.styleFrom(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              ),
              child: connecting
                  ? const SizedBox(
                      width: 22, height: 22,
                      child: CircularProgressIndicator(strokeWidth: 2.4, color: Colors.white),
                    )
                  : const Text('CONNECT TO CRM', style: TextStyle(fontWeight: FontWeight.w800)),
            ),
          ),
        ],
      ),
    );
  }
}
