import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/issue_request.dart';
import '../models/agent_response.dart';

class ApiService {
  final String baseUrl;
  final http.Client client;
  ApiService({this.baseUrl = 'http://localhost:8080', http.Client? client}) 
    : client = client ?? http.Client();

  Future<AgentResponse> analyzeIssue(IssueRequest request) async {
    final response = await this.client.post(
      Uri.parse('$baseUrl/agent/issue'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(request.toJson()),
    ).timeout(const Duration(seconds: 30));

    if (response.statusCode == 200) {
      return AgentResponse.fromJson(jsonDecode(response.body));
    }
    throw Exception('API error: ${response.statusCode}');
  }

  Future<Map<String, dynamic>> confirmAction(String sessionId, String actionId, bool approved) async {
    final response = await this.client.post(
      Uri.parse('$baseUrl/agent/confirm-action'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'session_id': sessionId, 'action_id': actionId, 'approved': approved}),
    );
    return jsonDecode(response.body) as Map<String, dynamic>;
  }
}
