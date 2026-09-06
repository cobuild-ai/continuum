package ai.continuum.android.data.models

import com.google.gson.annotations.SerializedName

enum class TaskState {
    IDLE,
    ANALYZING_LENS,
    AWAITING_DESIGN_APPROVAL,
    SANDBOX_EXECUTING,
    DIFF_READY,
    AWAITING_MERGE_APPROVAL,
    MERGED,
    REJECTED,
    FAILED
}

data class FileDiff(
    val filepath: String,
    val additions: Int = 0,
    val deletions: Int = 0,
    val patch: String = ""
)

data class DiffSummary(
    @SerializedName("total_files_changed") val totalFilesChanged: Int = 0,
    @SerializedName("total_additions") val totalAdditions: Int = 0,
    @SerializedName("total_deletions") val totalDeletions: Int = 0,
    val files: List<FileDiff> = emptyList()
)

data class TaskCreateRequest(
    val prompt: String,
    @SerializedName("target_repo_path") val targetRepoPath: String? = null,
    @SerializedName("base_branch") val baseBranch: String = "main"
)

data class ApprovalRequest(
    val approved: Boolean,
    val feedback: String? = null
)

data class TaskResponse(
    val id: String,
    val prompt: String,
    val state: TaskState,
    @SerializedName("branch_name") val branchName: String,
    @SerializedName("lens_report") val lensReport: LensReport? = null,
    @SerializedName("diff_summary") val diffSummary: DiffSummary? = null,
    @SerializedName("error_message") val errorMessage: String? = null,
    @SerializedName("created_at") val createdAt: String? = null,
    @SerializedName("updated_at") val updatedAt: String? = null
)

data class ProjectInfo(
    val name: String,
    val path: String,
    @SerializedName("current_branch") val currentBranch: String = "main",
    @SerializedName("is_git") val isGit: Boolean = true,
    @SerializedName("is_clean") val isClean: Boolean = true,
    val description: String = ""
)

data class ProjectSelectRequest(
    val path: String
)

data class ChatMessage(
    val id: String = java.util.UUID.randomUUID().toString(),
    val text: String,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis(),
    val task: TaskResponse? = null,
    val isError: Boolean = false,
    val errorMessage: String? = null
)

