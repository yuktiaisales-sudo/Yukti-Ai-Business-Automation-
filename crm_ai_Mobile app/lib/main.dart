import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CRM AI Dashboard',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: DashboardScreen(),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {

  String selectedMonth = "This Month";
  String selectedProject = "All";

  int totalLeads = 0;
  int todayLeads = 0;

  @override
  void initState() {
    super.initState();
    fetchData();
  }

  Future<void> fetchData() async {
    try {
      final response = await http.get(
        Uri.parse("http://10.0.2.2:5050/api/data?month=$selectedMonth&project=$selectedProject"),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        setState(() {
          totalLeads = data['total_leads'];
          todayLeads = data['today_leads'];
        });
      }
    } catch (e) {
      print("Error: $e");
    }
  }

  Widget buildCard(String title, int value) {
    return Card(
      elevation: 4,
      child: Container(
        width: 150,
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Text(title, style: TextStyle(fontSize: 16)),
            SizedBox(height: 10),
            Text(value.toString(),
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("CRM AI Dashboard"),
      ),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [

            /// Month Dropdown
            DropdownButton<String>(
              value: selectedMonth,
              items: ["Today", "This Week", "This Month", "Last Month"]
                  .map((e) => DropdownMenuItem(
                        value: e,
                        child: Text(e),
                      ))
                  .toList(),
              onChanged: (value) {
                setState(() {
                  selectedMonth = value!;
                });
                fetchData();
              },
            ),

            /// Project Dropdown
            DropdownButton<String>(
              value: selectedProject,
              items: ["All", "Pride Towers", "San Lucas", "San Martin"]
                  .map((e) => DropdownMenuItem(
                        value: e,
                        child: Text(e),
                      ))
                  .toList(),
              onChanged: (value) {
                setState(() {
                  selectedProject = value!;
                });
                fetchData();
              },
            ),

            SizedBox(height: 20),

            /// Cards
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                buildCard("Total Leads", totalLeads),
                buildCard("Today Leads", todayLeads),
              ],
            ),
          ],
        ),
      ),
    );
  }
}