package com.supportsight.actions;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class RootController {

    @GetMapping("/")
    public String root() {
        return "{\"status\":\"ok\",\"service\":\"actions-service\"}";
    }
}
