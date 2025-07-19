// ECGPredictionApplication.java
package com.ecgprediction;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ECGPredictionApplication {
    public static void main(String[] args) {
        SpringApplication.run(ECGPredictionApplication.class, args);
    }
}

// User.java
package com.ecgprediction.model;

import jakarta.persistence.*;

@Entity
public class User {
    @Id
    private String id;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private String answer1;

    @Column(nullable = false)
    private String answer2;

    // Getters and Setters
}

// UserRepository.java
package com.ecgprediction.repository;

import com.ecgprediction.model.User;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, String> {}

// WebSecurityConfig.java
package com.ecgprediction.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class WebSecurityConfig {
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf().disable()
            .authorizeHttpRequests()
            .requestMatchers("/login", "/register", "/forgot_password", "/css/**").permitAll()
            .anyRequest().authenticated()
            .and().formLogin().loginPage("/login").defaultSuccessUrl("/dashboard", true);
        return http.build();
    }
}

// UserController.java
package com.ecgprediction.controller;

import com.ecgprediction.model.User;
import com.ecgprediction.repository.UserRepository;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Controller
public class UserController {
    @Autowired private UserRepository userRepo;
    @Autowired private PasswordEncoder encoder;

    @GetMapping("/login")
    public String loginPage() { return "login"; }

    @GetMapping("/register")
    public String registerPage() { return "register"; }

    @PostMapping("/register")
    public String register(@RequestParam String username, @RequestParam String password,
                           @RequestParam String answer1, @RequestParam String answer2) {
        if (userRepo.existsById(username)) return "register";
        User user = new User();
        user.setId(username);
        user.setPassword(encoder.encode(password));
        user.setAnswer1(answer1);
        user.setAnswer2(answer2);
        userRepo.save(user);
        return "redirect:/login";
    }

    @GetMapping("/forgot_password")
    public String forgotPasswordPage() { return "forgot_password"; }

    @PostMapping("/forgot_password")
    public String verifySecurity(@RequestParam String username,
                                 @RequestParam String answer1, @RequestParam String answer2,
                                 HttpSession session) {
        User user = userRepo.findById(username).orElse(null);
        if (user != null && user.getAnswer1().equals(answer1) && user.getAnswer2().equals(answer2)) {
            session.setAttribute("reset_user", username);
            return "redirect:/reset_password";
        }
        return "forgot_password";
    }

    @GetMapping("/reset_password")
    public String resetPage() { return "reset_password"; }

    @PostMapping("/reset_password")
    public String resetPassword(@RequestParam String password, HttpSession session) {
        String username = (String) session.getAttribute("reset_user");
        User user = userRepo.findById(username).orElse(null);
        if (user != null) {
            user.setPassword(encoder.encode(password));
            userRepo.save(user);
        }
        return "redirect:/login";
    }
}

// DashboardController.java
package com.ecgprediction.controller;

import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Controller
public class DashboardController {

    @GetMapping("/dashboard")
    public String dashboard() { return "dashboard"; }

    @PostMapping("/questions")
    public String submitSymptoms(@RequestParam Map<String, String> symptoms, HttpSession session) {
        session.setAttribute("symptoms", symptoms);
        return "redirect:/result";
    }

    @PostMapping("/predict")
    public String predict(@RequestParam Map<String, String> ecgData, HttpSession session, Model model) {
        RestTemplate restTemplate = new RestTemplate();
        String result = restTemplate.postForObject("http://localhost:5000/predict", ecgData, String.class); // assuming Python Flask on port 5000

        @SuppressWarnings("unchecked")
        Map<String, String> symptoms = (Map<String, String>) session.getAttribute("symptoms");
        long yesCount = symptoms.values().stream().filter(val -> val.equals("1")).count();

        String suggestion;
        if (yesCount >= 3) suggestion = "High risk. Consult doctor.";
        else if (yesCount == 2) suggestion = "Monitor symptoms.";
        else if (yesCount == 1) suggestion = "Mild. Stay healthy.";
        else if (result.contains("Normal")) suggestion = "You are healthy.";
        else suggestion = "Visit a physician promptly.";

        model.addAttribute("result", result);
        model.addAttribute("suggestion", suggestion);
        return "result";
    }
}

// application.properties
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
spring.thymeleaf.prefix=classpath:/templates/
spring.thymeleaf.suffix=.html
