class Hypothesis {
  final String description;
  final double confidence;
  final List<String> evidence;
  Hypothesis({required this.description, required this.confidence, required this.evidence});
  factory Hypothesis.fromJson(Map<String, dynamic> j) => Hypothesis(
    description: j['description'] ?? '',
    confidence: (j['confidence'] as num?)?.toDouble() ?? 0.0,
    evidence: List<String>.from(j['evidence'] ?? []),
  );
}

class SuggestedAction {
  final String id, title, description;
  final bool requiresConfirmation, isDestructive;
  SuggestedAction({required this.id, required this.title, required this.description,
    required this.requiresConfirmation, required this.isDestructive});
  factory SuggestedAction.fromJson(Map<String, dynamic> j) => SuggestedAction(
    id: j['id'] ?? '', title: j['title'] ?? '', description: j['description'] ?? '',
    requiresConfirmation: j['requires_confirmation'] ?? true,
    isDestructive: j['is_destructive'] ?? false,
  );
}

class AgentResponse {
  final String sessionId, correlationId, whatIUnderstood;
  final String? whatISee, rootCauseSummary, nextAction;
  final List<String> recommendations;
  final List<Hypothesis> hypotheses;
  final double confidence;
  final bool needsMoreInfo;
  final List<SuggestedAction> suggestedActions;

  AgentResponse({required this.sessionId, required this.correlationId,
    required this.whatIUnderstood, this.whatISee, this.rootCauseSummary, this.nextAction,
    required this.recommendations, required this.hypotheses,
    required this.confidence, required this.needsMoreInfo,
    required this.suggestedActions});

  factory AgentResponse.fromJson(Map<String, dynamic> j) => AgentResponse(
    sessionId: j['session_id'] ?? '',
    correlationId: j['correlation_id'] ?? '',
    whatIUnderstood: j['what_i_understood'] ?? '',
    whatISee: j['what_i_see'],
    rootCauseSummary: j['root_cause_summary'],
    nextAction: j['next_action'],
    recommendations: List<String>.from(j['recommendations'] ?? []),
    hypotheses: (j['hypotheses'] as List? ?? []).map((h) => Hypothesis.fromJson(h)).toList(),
    confidence: (j['confidence'] as num?)?.toDouble() ?? 0.0,
    needsMoreInfo: j['needs_more_info'] ?? false,
    suggestedActions: (j['suggested_actions'] as List? ?? []).map((a) => SuggestedAction.fromJson(a)).toList(),
  );
}
