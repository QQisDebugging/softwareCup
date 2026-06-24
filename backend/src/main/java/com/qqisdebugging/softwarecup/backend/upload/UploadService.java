package com.qqisdebugging.softwarecup.backend.upload;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.qqisdebugging.softwarecup.backend.agent.AgentArtifactService;
import com.qqisdebugging.softwarecup.backend.config.StorageProperties;
import com.qqisdebugging.softwarecup.backend.course.CourseService;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
public class UploadService {
    private final UploadedAssetRepository repository;
    private final CourseService courseService;
    private final AgentArtifactService agentArtifactService;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final Path storageRoot;

    public UploadService(
            UploadedAssetRepository repository,
            CourseService courseService,
            AgentArtifactService agentArtifactService,
            StorageProperties storageProperties) {
        this.repository = repository;
        this.courseService = courseService;
        this.agentArtifactService = agentArtifactService;
        this.storageRoot = storageProperties.getRoot().toAbsolutePath().normalize();
    }

    @Transactional
    public UploadAssetResponse store(MultipartFile file, String purpose) {
        return storeAsset(file, purpose, null, "student", false);
    }

    @Transactional
    public UploadAssetResponse storeCourseMaterial(MultipartFile file, String courseId, String uploaderRole) {
        if (courseId != null && !courseId.isBlank()) {
            courseService.requireCourse(courseId);
        }
        return storeAsset(file, "course-material", courseId, uploaderRole, true);
    }

    private UploadAssetResponse storeAsset(MultipartFile file, String purpose, String courseId, String uploaderRole, boolean analyze) {
        if (file.isEmpty()) {
            throw new IllegalArgumentException("Uploaded file is empty");
        }
        try {
            String safeName = sanitize(file.getOriginalFilename());
            String storedName = UUID.randomUUID() + "-" + safeName;
            Path dateDir = storageRoot.resolve(LocalDate.now().toString()).normalize();
            Files.createDirectories(dateDir);
            Path target = dateDir.resolve(storedName).normalize();
            if (!target.startsWith(storageRoot)) {
                throw new IllegalArgumentException("Invalid storage path");
            }
            file.transferTo(target);
            MaterialAnalysis analysis = analyze ? analyzeMaterial(target, safeName, file.getContentType(), uploaderRole, courseId) : storedOnly(safeName);
            UploadedAsset saved = repository.save(new UploadedAsset(
                    safeName,
                    file.getContentType() == null ? "application/octet-stream" : file.getContentType(),
                    file.getSize(),
                    storageRoot.relativize(target).toString(),
                    purpose,
                    courseId,
                    normalizeRole(uploaderRole),
                    analysis.materialType(),
                    analysis.parseStatus(),
                    analysis.parseMessage(),
                    analysis.extractedTextPreview(),
                    writeJson(analysis.knowledgePoints()),
                    writeJson(analysis.courseDraft())));
            return UploadAssetResponse.from(saved);
        } catch (IOException ex) {
            throw new IllegalStateException("Failed to store uploaded file: " + ex.getMessage(), ex);
        }
    }

    @Transactional(readOnly = true)
    public List<UploadAssetResponse> listUploads() {
        return repository.findAll().stream()
                .sorted(Comparator.comparing(UploadedAsset::getCreatedAt).reversed())
                .map(UploadAssetResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<UploadAssetResponse> listCourseMaterials(String courseId) {
        if (courseId == null || courseId.isBlank()) {
            return listUploads().stream()
                    .filter(item -> "course-material".equals(item.purpose()))
                    .toList();
        }
        return repository.findByCourseIdOrderByCreatedAtDesc(courseId).stream()
                .map(UploadAssetResponse::from)
                .toList();
    }

    @Transactional
    public UploadAssetResponse reparseCourseMaterial(String assetId) {
        UploadedAsset asset = requireCourseMaterial(assetId);
        Path stored = resolveStoredPath(asset);
        if (!Files.exists(stored)) {
            throw new IllegalStateException("Uploaded course material file is missing on disk");
        }
        MaterialAnalysis analysis = analyzeMaterial(
                stored,
                asset.getOriginalFilename(),
                asset.getContentType(),
                asset.getUploaderRole(),
                asset.getCourseId());
        asset.replaceAnalysis(
                analysis.materialType(),
                analysis.parseStatus(),
                analysis.parseMessage(),
                analysis.extractedTextPreview(),
                writeJson(analysis.knowledgePoints()),
                writeJson(analysis.courseDraft()));
        return UploadAssetResponse.from(asset);
    }

    @Transactional
    public void deleteCourseMaterial(String assetId) {
        UploadedAsset asset = requireCourseMaterial(assetId);
        Path stored = resolveStoredPath(asset);
        try {
            Files.deleteIfExists(stored);
        } catch (IOException ex) {
            throw new IllegalStateException("Failed to delete uploaded course material file: " + ex.getMessage(), ex);
        }
        repository.delete(asset);
    }

    private UploadedAsset requireCourseMaterial(String assetId) {
        UploadedAsset asset = repository.findById(assetId)
                .orElseThrow(() -> new IllegalArgumentException("Course material upload not found: " + assetId));
        if (!"course-material".equals(asset.getPurpose())) {
            throw new IllegalArgumentException("Upload is not a course material: " + assetId);
        }
        return asset;
    }

    private Path resolveStoredPath(UploadedAsset asset) {
        Path stored = storageRoot.resolve(asset.getStoragePath()).normalize();
        if (!stored.startsWith(storageRoot)) {
            throw new IllegalArgumentException("Invalid stored upload path");
        }
        return stored;
    }

    private String sanitize(String filename) {
        String value = filename == null || filename.isBlank() ? "upload.bin" : filename;
        return value.replaceAll("[\\\\/:*?\"<>|]", "_");
    }

    private MaterialAnalysis storedOnly(String filename) {
        return new MaterialAnalysis(inferMaterialType(filename, ""), "STORED", "文件已保存。", "", List.of(), Map.of());
    }

    private MaterialAnalysis analyzeMaterial(Path target, String filename, String contentType, String uploaderRole, String courseId) {
        String materialType = inferMaterialType(filename, contentType);
        String extracted = "";
        String status = "ANALYZED";
        String message = "资料已保存，并由课程结构智能体生成章节、知识点和资源槽位建议。";
        try {
            extracted = extractText(target, filename, contentType);
            if (extracted.isBlank()) {
                message = "资料已保存；当前文件格式未提取到稳定正文，课程结构智能体已基于文件名、类型和元数据生成建议。";
            }
        } catch (IOException ex) {
            message = "资料已保存；正文解析失败，课程结构智能体已基于文件名、类型和元数据生成建议。解析错误：" + ex.getMessage();
        }
        String preview = compact(extracted.isBlank() ? filename.replaceAll("\\.[^.]+$", "") : extracted, 1800);
        List<String> seedKnowledgePoints = extractKnowledgePoints(filename, extracted);
        Map<String, Object> courseDraft = buildCourseDraftWithAgent(filename, materialType, seedKnowledgePoints, preview, uploaderRole, courseId);
        List<String> knowledgePoints = stringList(courseDraft.get("knowledgePoints"));
        if (knowledgePoints.isEmpty()) {
            throw new IllegalStateException("Course structure agent returned no knowledge points");
        }
        return new MaterialAnalysis(materialType, status, message, preview, knowledgePoints, courseDraft);
    }

    private String extractText(Path target, String filename, String contentType) throws IOException {
        String extension = extension(filename);
        if (List.of("txt", "md", "csv", "json", "xml", "java", "py", "js", "ts").contains(extension)) {
            return readTextFile(target);
        }
        if (List.of("pptx", "docx", "xlsx").contains(extension)) {
            return extractOoxmlText(target, extension);
        }
        if ("pdf".equals(extension) || (contentType != null && contentType.toLowerCase(Locale.ROOT).contains("pdf"))) {
            return extractPdfText(target);
        }
        return "";
    }

    private String readTextFile(Path target) throws IOException {
        byte[] bytes;
        try (InputStream input = Files.newInputStream(target)) {
            bytes = input.readNBytes(400_000);
        }
        try {
            return normalizeWhitespace(decodeText(bytes, StandardCharsets.UTF_8));
        } catch (CharacterCodingException ex) {
            return normalizeWhitespace(decodeText(bytes, Charset.forName("GB18030")));
        }
    }

    private String decodeText(byte[] bytes, Charset charset) throws CharacterCodingException {
        return charset.newDecoder()
                .onMalformedInput(CodingErrorAction.REPORT)
                .onUnmappableCharacter(CodingErrorAction.REPORT)
                .decode(ByteBuffer.wrap(bytes))
                .toString();
    }

    private String extractOoxmlText(Path target, String extension) throws IOException {
        StringBuilder builder = new StringBuilder();
        try (ZipInputStream zip = new ZipInputStream(Files.newInputStream(target))) {
            ZipEntry entry;
            while ((entry = zip.getNextEntry()) != null && builder.length() < 120_000) {
                String name = entry.getName();
                if (!entry.isDirectory() && name.endsWith(".xml") && isRelevantOoxmlEntry(name, extension)) {
                    String xml = new String(zip.readNBytes(180_000), StandardCharsets.UTF_8);
                    builder.append(' ').append(stripXml(xml));
                }
            }
        }
        return normalizeWhitespace(builder.toString());
    }

    private boolean isRelevantOoxmlEntry(String name, String extension) {
        if ("pptx".equals(extension)) {
            return name.startsWith("ppt/slides/") || name.startsWith("ppt/notesSlides/") || name.startsWith("ppt/comments/");
        }
        if ("docx".equals(extension)) {
            return name.startsWith("word/");
        }
        if ("xlsx".equals(extension)) {
            return name.startsWith("xl/sharedStrings") || name.startsWith("xl/worksheets/");
        }
        return true;
    }

    private String extractPdfText(Path target) throws IOException {
        byte[] bytes;
        try (InputStream input = Files.newInputStream(target)) {
            bytes = input.readNBytes(1_000_000);
        }
        String raw = new String(bytes, StandardCharsets.ISO_8859_1);
        Matcher matcher = Pattern.compile("\\(([^()]{2,240})\\)").matcher(raw);
        List<String> parts = new ArrayList<>();
        while (matcher.find() && parts.size() < 180) {
            String value = matcher.group(1)
                    .replace("\\(", "(")
                    .replace("\\)", ")")
                    .replace("\\n", " ")
                    .replace("\\r", " ");
            value = normalizeWhitespace(value.replaceAll("[^\\p{IsHan}\\p{L}\\p{N}\\p{Punct}\\s]", " "));
            if (value.length() >= 2 && value.chars().anyMatch(Character::isLetterOrDigit)) {
                parts.add(value);
            }
        }
        return normalizeWhitespace(String.join(" ", parts));
    }

    private String stripXml(String xml) {
        return decodeXml(xml
                .replaceAll("<[^>]+>", " ")
                .replaceAll("\\s+", " "));
    }

    private String decodeXml(String value) {
        return value
                .replace("&lt;", "<")
                .replace("&gt;", ">")
                .replace("&amp;", "&")
                .replace("&quot;", "\"")
                .replace("&apos;", "'");
    }

    private String inferMaterialType(String filename, String contentType) {
        String extension = extension(filename);
        String type = contentType == null ? "" : contentType.toLowerCase(Locale.ROOT);
        if (List.of("ppt", "pptx").contains(extension) || type.contains("presentation")) return "PPT_COURSEWARE";
        if (List.of("pdf", "epub").contains(extension) || type.contains("pdf")) return "TEXTBOOK";
        if (List.of("doc", "docx", "txt", "md").contains(extension)) return "HANDOUT";
        if (List.of("xls", "xlsx", "csv").contains(extension)) return "QUESTION_BANK";
        return "FILE";
    }

    private List<String> extractKnowledgePoints(String filename, String extracted) {
        LinkedHashSet<String> points = new LinkedHashSet<>();
        String text = (filename + "\n" + extracted).toLowerCase(Locale.ROOT);
        Map<String, String> known = Map.ofEntries(
                Map.entry("spring boot", "Spring Boot"),
                Map.entry("controller", "Controller 分层"),
                Map.entry("service", "Service 业务逻辑"),
                Map.entry("repository", "Repository 数据访问"),
                Map.entry("rest", "REST API"),
                Map.entry("dto", "DTO 数据传输"),
                Map.entry("http", "HTTP 请求响应"),
                Map.entry("database", "数据库访问"),
                Map.entry("sql", "SQL 与数据建模"),
                Map.entry("file upload", "文件上传"),
                Map.entry("test", "测试与质量保障"),
                Map.entry("deployment", "部署与运维"),
                Map.entry("多智能体", "多智能体协同"),
                Map.entry("大模型", "大模型辅助学习"),
                Map.entry("个性化", "个性化学习资源"));
        known.forEach((key, value) -> {
            if (text.contains(key)) points.add(value);
        });

        for (String segment : (filename + "\n" + extracted).split("[\\n。；;，,、：:（）()\\[\\]{}<>]+")) {
            String value = normalizeWhitespace(segment);
            if (value.length() >= 3 && value.length() <= 28 && !value.matches("\\d+") && points.size() < 8) {
                points.add(value);
            }
            if (points.size() >= 8) break;
        }
        if (points.isEmpty()) {
            points.add(filename.replaceAll("\\.[^.]+$", ""));
        }
        return List.copyOf(points).subList(0, Math.min(8, points.size()));
    }

    private Map<String, Object> buildCourseDraftWithAgent(
            String filename,
            String materialType,
            List<String> seedKnowledgePoints,
            String preview,
            String uploaderRole,
            String courseId) {
        String role = normalizeRole(uploaderRole);
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("courseId", courseId == null ? "" : courseId);
        payload.put("courseTitle", filename.replaceAll("\\.[^.]+$", ""));
        payload.put("sourceFile", filename);
        payload.put("materialType", materialType);
        payload.put("uploaderRole", role);
        payload.put("extractedText", preview);
        payload.put("knownKnowledgePoints", seedKnowledgePoints);
        payload.put("targetLearners", role.equals("teacher") ? "班级学生" : "个人学习者");
        payload.put("desiredWeeks", 8);
        payload.put("documentTexts", preview.isBlank() ? List.of(filename) : List.of(preview));
        Map<String, Object> response = agentArtifactService.invokeAndStore(
                "COURSE_STRUCTURE",
                "/agents/course/structure",
                payload);
        List<String> knowledgePointNames = namesFromKnowledgePoints(response.get("knowledgePoints"));
        Map<String, Object> draft = new LinkedHashMap<>();
        draft.put("agentEndpoint", "/agents/course/structure");
        draft.put("agentArtifactId", response.get("artifactId"));
        draft.put("agentStatus", response.get("artifactStatus"));
        draft.put("summary", response.get("summary"));
        draft.put("source", role.equals("teacher") ? "teacher_material_import" : "student_self_course_upload");
        draft.put("sourceFile", filename);
        draft.put("materialType", materialType);
        draft.put("suggestedTitle", valueOrFallback(textValue(response.get("suggestedTitle")), filename.replaceAll("\\.[^.]+$", "") + " 自建课程"));
        draft.put("suggestedDepartment", valueOrFallback(textValue(response.get("suggestedDepartment")), role.equals("teacher") ? "课程教师导入" : "学生个人课程"));
        draft.put("suggestedCreditHours", intValue(response.get("suggestedCreditHours"), Math.max(16, knowledgePointNames.size() * 4)));
        draft.put("suggestedDescription", valueOrFallback(textValue(response.get("suggestedDescription")), "基于《" + filename + "》构建课程知识库。"));
        draft.put("learningObjectives", response.get("learningObjectives"));
        draft.put("chapters", response.get("chapters"));
        draft.put("resourceSlots", response.get("resourceSlots"));
        draft.put("publishChecks", response.get("publishChecks"));
        draft.put("citations", response.get("citations"));
        draft.put("knowledgePoints", knowledgePointNames);
        draft.put("textPreview", compact(preview, 600));
        draft.put("knowledgeBuildFlow", List.of("资料上传", "正文解析", "课程结构智能体", "章节知识点生成", "资源槽位规划", "发布检查", "学习推送"));
        draft.put("weeks", response.get("weeks"));
        return draft;
    }

    private List<String> namesFromKnowledgePoints(Object value) {
        List<String> names = new ArrayList<>();
        if (value instanceof List<?> items) {
            for (Object item : items) {
                if (item instanceof Map<?, ?> map) {
                    String name = textValue(map.get("name"));
                    if (name != null && !name.isBlank()) {
                        names.add(name);
                    }
                } else if (item != null) {
                    names.add(String.valueOf(item));
                }
            }
        }
        return List.copyOf(new LinkedHashSet<>(names));
    }

    private List<String> stringList(Object value) {
        if (!(value instanceof List<?> items)) {
            return List.of();
        }
        List<String> result = new ArrayList<>();
        for (Object item : items) {
            if (item != null && !String.valueOf(item).isBlank()) {
                result.add(String.valueOf(item));
            }
        }
        return result;
    }

    private String textValue(Object value) {
        return value == null ? null : String.valueOf(value).trim();
    }

    private String valueOrFallback(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    private int intValue(Object value, int fallback) {
        try {
            return value == null ? fallback : Integer.parseInt(String.valueOf(value));
        } catch (NumberFormatException ex) {
            return fallback;
        }
    }

    private String normalizeRole(String uploaderRole) {
        return "teacher".equalsIgnoreCase(uploaderRole) ? "teacher" : "student";
    }

    private String extension(String filename) {
        int index = filename == null ? -1 : filename.lastIndexOf('.');
        return index < 0 ? "" : filename.substring(index + 1).toLowerCase(Locale.ROOT);
    }

    private String normalizeWhitespace(String value) {
        if (value == null) return "";
        return value
                .replace('\uFEFF', ' ')
                .replace('\u0000', ' ')
                .replaceAll("\\s+", " ")
                .trim();
    }

    private String compact(String value, int maxLength) {
        String normalized = normalizeWhitespace(value);
        return normalized.length() > maxLength ? normalized.substring(0, maxLength) : normalized;
    }

    private String writeJson(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException ex) {
            return "{}";
        }
    }

    private record MaterialAnalysis(
            String materialType,
            String parseStatus,
            String parseMessage,
            String extractedTextPreview,
            List<String> knowledgePoints,
            Map<String, Object> courseDraft) {
    }
}
