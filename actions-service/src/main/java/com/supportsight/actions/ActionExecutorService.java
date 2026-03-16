package com.supportsight.actions;

import com.supportsight.domain.ActionLog;
import com.supportsight.domain.ActionRequest;
import com.supportsight.domain.ActionResult;
import com.supportsight.infrastructure.ActionLogRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

/**
 * Enterprise Action Executor Service.
 * Implements high-solidity patterns: Audit trails, Allow-listing, and Dry-run validation.
 */
@Service
public class ActionExecutorService {

    private static final Logger log = LoggerFactory.getLogger(ActionExecutorService.class);

    // OWASP Strict Allowlist: only permitted action types can be executed
    public static final List<String> ALLOWED_ACTION_TYPES = List.of(
        "CHECK_SERVICE_STATUS",
        "FETCH_RECENT_LOGS",
        "PING_ENDPOINT",
        "GET_DISK_USAGE",
        "GET_MEMORY_USAGE",
        "CREATE_INCIDENT_TICKET",
        "GENERATE_INCIDENT_REPORT",
        "SECURITY_AUDIT",
        "RESTART_SERVICE"
    );

    private final ActionLogRepository logRepo;

    public ActionExecutorService(ActionLogRepository logRepo) {
        this.logRepo = logRepo;
    }

    /**
     * Executes the requested action with full auditing.
     */
    @Transactional
    public ActionResult execute(ActionRequest request) {
        // 1. Policy Enforcement (Enterprise Pattern)
        if (!ALLOWED_ACTION_TYPES.contains(request.actionType())) {
            String msg = "[SECURITY] Unauthorized action type: " + request.actionType();
            persist(request, "REJECTED", null, msg, true);
            return new ActionResult(request.actionId(), request.sessionId(),
                "REJECTED", null, msg, Instant.now());
        }

        // 2. Dry-run Mode (Safeguard Pattern)
        boolean isDryRun = request.parameters() != null && request.parameters().contains("--dry-run");
        if (isDryRun) {
            String dryRunMsg = "[DRY-RUN] Action validated. Would execute: " + request.actionType();
            persist(request, "DRY_RUN", dryRunMsg, null, false);
            return new ActionResult(request.actionId(), request.sessionId(),
                "DRY_RUN", dryRunMsg, null, Instant.now());
        }

        // 3. Execution with Error Handling
        try {
            log.info("Executing action {} for session {}", request.actionType(), request.sessionId());
            
            String output = switch (request.actionType()) {
                case "CHECK_SERVICE_STATUS"   -> simulateServiceCheck(request.parameters());
                case "FETCH_RECENT_LOGS"      -> "[DEMO] Last 10 log lines fetched successfully.";
                case "PING_ENDPOINT"          -> simulatePing(request.parameters());
                case "GET_DISK_USAGE"         -> "[DEMO] Disk: 72% used (18 GB / 25 GB)";
                case "GET_MEMORY_USAGE"       -> "[DEMO] Memory: 6.2 GB / 8 GB (77%)";
                case "CREATE_INCIDENT_TICKET" -> "[DEMO] Ticket #INC-2026-0315 created successfully.";
                case "GENERATE_INCIDENT_REPORT" -> buildReport(request);
                case "SECURITY_AUDIT"         -> "[DEMO] Security Scan: No open public ports found. SSH hardening active.";
                case "RESTART_SERVICE"        -> performRestart(request.parameters());
                default                       -> "Unknown action type.";
            };

            persist(request, "SUCCESS", output, null, false);
            return new ActionResult(request.actionId(), request.sessionId(),
                "SUCCESS", output, null, Instant.now());
                
        } catch (Exception e) {
            log.error("Action execution failed: {}", e.getMessage());
            persist(request, "FAILED", null, e.getMessage(), false);
            return new ActionResult(request.actionId(), request.sessionId(),
                "FAILED", null, e.getMessage(), Instant.now());
        }
    }

    private String simulateServiceCheck(String params) {
        return "[ENTERPRISE] Service '" + (params != null ? params : "unknown") + "' → STATUS: UP (latency 45ms)";
    }

    private String simulatePing(String params) {
        return "[ENTERPRISE] PING " + (params != null ? params : "localhost") + " → 3 packets sent, 0 lost (avg 2ms)";
    }

    private String buildReport(ActionRequest request) {
        return "# Enterprise Incident Report\nID: " + UUID.randomUUID() +
               "\nSession: " + request.sessionId() +
               "\nGenerated: " + Instant.now() +
               "\nStatus: Open (High Urgency)\n\n*Full report available via /session/{id}/report*";
    }

    private String performRestart(String params) {
        // In a real scenario, this would call a K8s API or systemctl
        return "[DANGER] Service '" + (params != null ? params : "main-app") + "' restarted. New PID: " + (1000 + (int)(Math.random() * 9000));
    }

    private void persist(ActionRequest req, String status, String output, String error, boolean isSecurityEvent) {
        ActionLog logEntry = new ActionLog(req.sessionId(), req.actionId(), req.actionType(), status, output, error);
        if (isSecurityEvent) {
            log.warn("[AUDIT] Security event recorded: {} for session {}", req.actionType(), req.sessionId());
        }
        logRepo.save(logEntry);
    }
}
