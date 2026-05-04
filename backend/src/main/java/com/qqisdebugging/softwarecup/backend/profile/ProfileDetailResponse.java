package com.qqisdebugging.softwarecup.backend.profile;

import java.util.List;

public record ProfileDetailResponse(
        ProfileResponse profile,
        List<ProfileDimensionResponse> dimensions,
        List<ProfileHistoryResponse> recentHistory) {
}
