package com.supportsight.actions;

import com.supportsight.domain.ActionLog;
import com.supportsight.domain.ActionRequest;
import com.supportsight.domain.ActionResult;
import com.supportsight.infrastructure.ActionLogRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;

@Service
public class ActionExecutorService {

    private static final Logger log = LoggerFactory.getLogger(ActionExecutorService.class);

    // Allowlist — OWASP: only permitted action types can be executed
    public static final List<String> ALLOWED_ACTION_TYPES = List.of(
        "CHECK_SERVICE_STATUS",
        "FETCH_RECENT_LOGS",
        "PING_ENDPOINT",
        "GET_DISK_USAGE",
        "GET_MEMORY_USAGE",
        "CREATE_INCIDENT_TICKET",
        "GENERATE_INCIDENT_REPORT",
        "SECURITY_AUDIT"
    );

    private final ActionLogRepository logRepo;

    public ActionExecutorService(ActionLogRepository logRepo) {
        this.logRepo = logRepo;
    }

    public ActionResult execute(ActionRequest request) {
        if (!ALLOWED_ACTION_TYPES.contains(request.actionType())) {
            String msg = "Action type not allowed: " + request.actionType();
            persist(request, "REJECTED", null, msg);
            return new ActionResult(request.actionId(), request.sessionId(),
                "REJECTED", null, msg, Instant.now());
        }
        try {
            String output = switch (request.actionType()) {
                case "CHECK_SERVICE_STATUS"   -> simulateServiceCheck(request.parameters());
                case "FETCH_RECENT_LOGS"      -> "[DEMO] Last 10 log lines fetched successfully.";
                case "PING_ENDPOINT"          -> simulatePing(request.parameters());
                case "GET_DISK_USAGE"         -> "[DEMO] Disk: 72% used (18 GB / 25 GB)";
                case "GET_MEMORY_USAGE"       -> "[DEMO] Memory: 6.2 GB / 8 GB (77%)";
                case "CREATE_INCIDENT_TICKET" -> "[DEMO] Ticket #INC-2026-0312 created.";
                case "GENERATE_INCIDENT_REPORT" -> buildReport(request);
                case "SECURITY_AUDIT"         -> "[DEMO] Security Scan: No open public ports found. SSH hardening active.";
                default                       -> "Unknown action type.";
            };
            persist(request, "SUCCESS", output, null);
            return new ActionResult(request.actionId(), request.sessionId(),
                "SUCCESS", output, null, Instant.now());
        } catch (Exception e) {
            log.error("Action execution failed: {}", e.getMessage());
            persist(request, "FAILED", null, e.getMessage());
            return new ActionResult(request.actionId(), request.sessionId(),
                "FAILED", null, e.getMessage(), Instant.now());
        }
    }

    private String simulateServiceCheck(String params) {
        return "[DEMO] Service '" + (params != null ? params : "unknown") + "' → STATUS: UP (latency 45ms)";
    }

    private String simulatePing(String params) {
        return "[DEMO] PING " + (params != null ? params : "localhost") + " → 3 packets sent, 0 lost";
    }

    private String buildReport(ActionRequest request) {
        return "# Incident Report\nSession: " + request.sessionId() +
               "\nGenerated: " + Instant.now() +
               "\nStatus: Open\n\n*Full report available via /session/{id}/report*";
    }

    private void persist(ActionRequest req, String status, String output, String error) {
        logRepo.save(new ActionLog(req.sessionId(), req.actionId(), req.actionType(), status, output, error));
    }
}
