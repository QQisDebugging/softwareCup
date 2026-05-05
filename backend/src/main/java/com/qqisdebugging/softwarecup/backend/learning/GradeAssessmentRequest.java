package com.qqisdebugging.softwarecup.backend.learning;

import com.qqisdebugging.softwarecup.backend.agent.AssessmentAnswer;
import com.qqisdebugging.softwarecup.backend.agent.AssessmentQuestion;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;
import java.util.List;

public record GradeAssessmentRequest(
        @NotBlank String studentProfileId,
        @NotBlank String courseId,
        @NotBlank @Size(max = 180) String topic,
        @Valid @NotEmpty List<AssessmentQuestion> questions,
        @Valid @NotEmpty List<AssessmentAnswer> answers) {
}
