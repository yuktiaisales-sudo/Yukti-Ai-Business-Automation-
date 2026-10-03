import 'package:flutter/material.dart';
import 'screen/crm_url_screen.dart';

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
