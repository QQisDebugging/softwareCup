package com.qqisdebugging.softwarecup.backend.profile;

import jakarta.validation.Valid;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/profiles")
public class ProfileController {
    private final ProfileService profileService;

    public ProfileController(ProfileService profileService) {
        this.profileService = profileService;
    }

    @PostMapping("/dialogue")
    ProfileResponse buildFromDialogue(@Valid @RequestBody BuildProfileRequest request) {
        return profileService.buildFromDialogue(request);
    }

    @GetMapping
    List<ProfileResponse> listProfiles() {
        return profileService.listProfiles();
    }

    @GetMapping("/{profileId}")
    ProfileResponse getProfile(@PathVariable String profileId) {
        return profileService.getProfile(profileId);
    }
}
