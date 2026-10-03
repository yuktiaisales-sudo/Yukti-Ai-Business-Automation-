import 'package:flutter/material.dart';
import 'dashboard.dart';

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

  Future<void> _connect() async {
    FocusScope.of(context).unfocus();

    if (_usernameController.text.trim().isEmpty ||
        _passwordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter username and password.'),
        ),
      );
      return;
    }

    setState(() => _connecting = true);

    // UI/navigation stage only.
    // Real CRM authentication will be connected next.
    await Future.delayed(const Duration(milliseconds: 700));

    if (!mounted) return;

    setState(() => _connecting = false);

    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(
        builder: (_) => const DashboardScreen(),
      ),
      (route) => false,
    );
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
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
      ),
    );
  }
}
