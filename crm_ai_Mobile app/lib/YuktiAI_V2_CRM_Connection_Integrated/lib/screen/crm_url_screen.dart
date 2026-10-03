import 'package:flutter/material.dart';
import '../services/crm_connection_service.dart';
import 'crm_login_screen.dart';

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
