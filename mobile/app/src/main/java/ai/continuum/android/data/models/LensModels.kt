package ai.continuum.android.data.models

import com.google.gson.annotations.SerializedName

enum class LensCategory(val value: String) {
    @SerializedName("clean_code")
    CLEAN_CODE("clean_code"),

    @SerializedName("clean_architecture")
    CLEAN_ARCHITECTURE("clean_architecture"),

    @SerializedName("security")
    SECURITY("security"),

    @SerializedName("performance")
    PERFORMANCE("performance"),

    @SerializedName("ai_conduct")
    AI_CONDUCT("ai_conduct")
}

data class FindingItem(
    val category: String,
    val severity: String,
    @SerializedName("principle_violated") val principleViolated: String,
    val description: String,
    val suggestion: String,
    val file: String? = null,
    val line: Int? = null
)

data class LensEvaluation(
    val category: String,
    @SerializedName("lens_name") val lensName: String,
    val passed: Boolean = false,
    val score: Int = 0,
    val findings: List<FindingItem> = emptyList(),
    val recommendations: List<String> = emptyList()
)

data class LensReport(
    @SerializedName("overall_passed") val overallPassed: Boolean,
    @SerializedName("average_score") val averageScore: Float,
    val evaluations: Map<String, LensEvaluation> = emptyMap(),
    val summary: String = ""
)
