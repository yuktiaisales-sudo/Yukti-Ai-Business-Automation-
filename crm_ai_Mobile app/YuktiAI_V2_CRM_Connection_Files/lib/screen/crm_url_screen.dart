import 'package:flutter/material.dart';
import '../services/crm_connection_service.dart';
import 'crm_login_screen.dart';

class CrmUrlScreen extends StatefulWidget {
  const CrmUrlScreen({super.key});

  @override
  State<CrmUrlScreen> createState() => _CrmUrlScreenState();
}

class _CrmUrlScreenState extends State<CrmUrlScreen> {
  final controller = TextEditingController();
  bool checking = false;
  String? error;

  Future<void> go() async {
    FocusScope.of(context).unfocus();
    setState(() { checking = true; error = null; });

    final result = await CrmConnectionService.validateCrmUrl(controller.text);
    if (!mounted) return;

    setState(() => checking = false);

    if (!result.success) {
      setState(() => error = result.message);
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => CrmLoginScreen(
          crmUrl: result.normalizedUrl ?? controller.text.trim(),
        ),
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
          padding: const EdgeInsets.all(26),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 38),
              Row(
                children: [
                  Container(
                    width: 52, height: 52,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(16),
                      gradient: const LinearGradient(
                        colors: [Color(0xFF3157D5), Color(0xFF7139C6)],
                      ),
                    ),
                    child: const Center(
                      child: Text('Y', style: TextStyle(
                        color: Colors.white, fontSize: 27, fontWeight: FontWeight.w900,
                      )),
                    ),
                  ),
                  const SizedBox(width: 14),
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('YUKTI-AI', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900)),
                      Text('Business Automation', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 65),
              const Text(
                'Connect your CRM',
                style: TextStyle(fontSize: 30, fontWeight: FontWeight.w800, letterSpacing: -0.8),
              ),
              const SizedBox(height: 10),
              Text(
                'Enter the CRM address you use on your laptop or PC.',
                style: TextStyle(fontSize: 15, height: 1.5, color: Colors.grey.shade600),
              ),
              const SizedBox(height: 30),
              const Text('CRM URL', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
              const SizedBox(height: 9),
              TextField(
                controller: controller,
                keyboardType: TextInputType.url,
                textInputAction: TextInputAction.go,
                onSubmitted: (_) => go(),
                decoration: InputDecoration(
                  hintText: 'https://your-crm.com',
                  prefixIcon: const Icon(Icons.language_rounded),
                  errorText: error,
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
                    borderSide: const BorderSide(color: Color(0xFF3157D5), width: 1.5),
                  ),
                ),
              ),
              const SizedBox(height: 18),
              SizedBox(
                height: 56,
                child: FilledButton(
                  onPressed: checking ? null : go,
                  style: FilledButton.styleFrom(
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: checking
                      ? const SizedBox(
                          width: 22, height: 22,
                          child: CircularProgressIndicator(strokeWidth: 2.4, color: Colors.white),
                        )
                      : const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text('GO', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
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
                    Icon(Icons.lock_outline_rounded, color: Colors.grey.shade700),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Your CRM credentials are requested only after the CRM URL step.',
                        style: TextStyle(fontSize: 12.5, height: 1.45, color: Colors.grey.shade700),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              Center(
                child: Text(
                  'YUKTI-AI  •  Business Automation',
                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Colors.grey.shade500),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
