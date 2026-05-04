package com.qqisdebugging.softwarecup.backend.profile;

import com.qqisdebugging.softwarecup.backend.common.NotFoundException;
import java.util.Comparator;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ProfileService {
    private final StudentProfileRepository profileRepository;

    public ProfileService(StudentProfileRepository profileRepository) {
        this.profileRepository = profileRepository;
    }

    @Transactional
    public ProfileResponse buildFromDialogue(BuildProfileRequest request) {
        String summary = summarizeDialogue(request.dialogueTurns());
        StudentProfile profile = new StudentProfile(
                request.studentName(),
                request.major(),
                request.currentLevel(),
                request.learningGoal(),
                request.preferences(),
                request.constraintsText(),
                summary);
        return ProfileResponse.from(profileRepository.save(profile));
    }

    @Transactional(readOnly = true)
    public List<ProfileResponse> listProfiles() {
        return profileRepository.findAll().stream()
                .sorted(Comparator.comparing(StudentProfile::getCreatedAt).reversed())
                .map(ProfileResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public ProfileResponse getProfile(String profileId) {
        return ProfileResponse.from(requireProfile(profileId));
    }

    public StudentProfile requireProfile(String profileId) {
        return profileRepository.findById(profileId)
                .orElseThrow(() -> new NotFoundException("Student profile not found: " + profileId));
    }

    private String summarizeDialogue(List<String> dialogueTurns) {
        String joined = String.join("\n", dialogueTurns);
        if (joined.length() <= 1200) {
            return joined;
        }
        return joined.substring(0, 1200) + "...";
    }
}
