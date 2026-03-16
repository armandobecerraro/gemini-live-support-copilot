import 'package:flutter/material.dart';
import '../models/issue_request.dart';
import '../models/agent_response.dart';
import '../services/api_service.dart';
import '../widgets/response_panel.dart';
import '../widgets/input_panel.dart';

class HomeScreen extends StatefulWidget {
  final ApiService? api;
  const HomeScreen({super.key, this.api});
  @override State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final ApiService _api;
  final _descController = TextEditingController();
  final _logsController = TextEditingController();
  AgentResponse? _response;
  bool _loading = false;
  String? _error;
  String? _sessionId;

  @override
  void initState() {
    super.initState();
    _api = widget.api ?? ApiService();
  }

  Future<void> _analyze() async {
    if (_descController.text.trim().isEmpty) return;
    setState(() { _loading = true; _error = null; });
    try {
      final result = await _api.analyzeIssue(IssueRequest(
        description: _descController.text,
        logs: _logsController.text.isEmpty ? null : _logsController.text,
        sessionId: _sessionId,
      ));
      setState(() { _response = result; _sessionId = result.sessionId; _loading = false; });
    } catch (e) {
      setState(() { _error = e.toString(); _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1117),
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B22),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('SupportSight Live', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            const Text('Multimodal Incident Agent · Gemini', style: TextStyle(color: Color(0xFF4F98A3), fontSize: 12)),
          ],
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: LayoutBuilder(
          builder: (context, constraints) {
            final isWide = constraints.maxWidth > 800;
            return isWide
              ? Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Expanded(child: InputPanel(descController: _descController, logsController: _logsController, loading: _loading, onAnalyze: _analyze, error: _error)),
                  const SizedBox(width: 16),
                  Expanded(child: ResponsePanel(response: _response, loading: _loading, api: _api)),
                ])
              : SingleChildScrollView(child: Column(children: [
                  InputPanel(descController: _descController, logsController: _logsController, loading: _loading, onAnalyze: _analyze, error: _error),
                  const SizedBox(height: 16),
                  ResponsePanel(response: _response, loading: _loading, api: _api),
                ]));
          },
        ),
      ),
    );
  }
}
