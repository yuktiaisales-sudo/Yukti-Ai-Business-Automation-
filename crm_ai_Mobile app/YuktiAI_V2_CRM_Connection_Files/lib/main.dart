import 'package:flutter/material.dart';
import 'screen/crm_url_screen.dart';

void main() => runApp(const YuktiAiApp());

class YuktiAiApp extends StatelessWidget {
  const YuktiAiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'YUKTI-AI',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF3157D5)),
        scaffoldBackgroundColor: const Color(0xFFF7F8FC),
      ),
      home: const CrmUrlScreen(),
    );
  }
}
