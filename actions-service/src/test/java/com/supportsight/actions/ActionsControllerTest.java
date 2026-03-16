package com.supportsight.actions;

import com.supportsight.domain.ActionRequest;
import com.supportsight.domain.ActionResult;
import com.supportsight.infrastructure.ActionLogRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.time.Instant;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.hamcrest.Matchers.hasItem;

@SpringBootTest
@AutoConfigureMockMvc
public class ActionsControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private ActionLogRepository logRepo;

    @Test
    public void testRootEndpoint() throws Exception {
        mockMvc.perform(get("/"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.service").value("actions-service"));
    }

    @Test
    public void testHealthEndpoint() throws Exception {
        mockMvc.perform(get("/actions/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("ok"));
    }

    @Test
    public void testAllowedTypes() throws Exception {
        mockMvc.perform(get("/actions/allowed-types")
                .header("X-API-Key", "change-me"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$", hasItem("RESTART_SERVICE")));
    }

    @Test
    public void testExecuteActionSuccess() throws Exception {
        ActionRequest request = new ActionRequest(
                UUID.randomUUID().toString(),
                "session-123",
                "CHECK_SERVICE_STATUS",
                "my-service"
        );

        mockMvc.perform(post("/actions/execute")
                .header("X-API-Key", "change-me")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("SUCCESS"))
                .andExpect(jsonPath("$.output").isNotEmpty());
    }

    @Test
    public void testExecuteActionUnauthorized() throws Exception {
        ActionRequest request = new ActionRequest(
                UUID.randomUUID().toString(),
                "session-123",
                "DELETE_ALL_DATABASES",
                null
        );

        mockMvc.perform(post("/actions/execute")
                .header("X-API-Key", "change-me")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("REJECTED"));
    }

    @Test
    public void testExecuteActionDryRun() throws Exception {
        ActionRequest request = new ActionRequest(
                UUID.randomUUID().toString(),
                "session-123",
                "RESTART_SERVICE",
                "--dry-run"
        );

        mockMvc.perform(post("/actions/execute")
                .header("X-API-Key", "change-me")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("DRY_RUN"));
    }

    @Test
    public void testExecuteAllAllowedTypes() throws Exception {
        String[] types = {
            "FETCH_RECENT_LOGS", "PING_ENDPOINT", "GET_DISK_USAGE",
            "GET_MEMORY_USAGE", "CREATE_INCIDENT_TICKET", "GENERATE_INCIDENT_REPORT",
            "SECURITY_AUDIT", "RESTART_SERVICE"
        };

        for (String type : types) {
            ActionRequest request = new ActionRequest(
                    UUID.randomUUID().toString(),
                    "session-123",
                    type,
                    null
            );

            mockMvc.perform(post("/actions/execute")
                    .header("X-API-Key", "change-me")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.status").value("SUCCESS"));
        }
    }
}
