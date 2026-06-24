package com.qqisdebugging.softwarecup.backend.learning;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LearningConversationMessageRepository extends JpaRepository<LearningConversationMessage, String> {
    List<LearningConversationMessage> findByConversationIdOrderByCreatedAtAscIdAsc(String conversationId);

    void deleteByConversationId(String conversationId);
}
